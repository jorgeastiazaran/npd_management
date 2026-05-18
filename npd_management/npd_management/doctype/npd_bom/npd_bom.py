# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from npd_management.api.npd_utils import get_erpnext_item_cost, get_erpnext_item

class NPDBOM(Document):
    def validate(self):
        self._ensure_item_doctypes()
        self.calculate_cost()
        self.calculate_nutritional_info()

    def _ensure_item_doctypes(self):
        """Auto-set item_doctype on rows where it is missing, so Dynamic Link validation passes."""
        default_type = getattr(self, "default_item_doctype", None) or "NPD Item"
        for row in self.items:
            if not row.item_doctype:
                row.item_doctype = default_type

    @frappe.whitelist()
    def get_bom_material_detail(self, args=None):
        """
        Mirror of ERPNext BOM.get_bom_material_detail().
        """
        import json
        if not args:
            args = frappe.form_dict
            
        if isinstance(args, str):
            args = json.loads(args)

        # Handle nested 'args' if passed from JS
        if "args" in args:
            args = args["args"]

        frappe.log_error(f"NPD BOM Processed Args: {args}", "NPD Debug")
        
        item_code = args.get("item_code")
        item_doctype = args.get("item_doctype") or "NPD Item"

        if item_doctype == "NPD Item" and frappe.db.exists("NPD Item", item_code):
            item = frappe.db.get_value(
                "NPD Item", item_code,
                ["item_name", "description", "stock_uom", "valuation_rate"],
                as_dict=True
            ) or {}
        else:
            # Check local Item first
            item = frappe.db.get_value(
                "Item", item_code,
                ["item_name", "description", "stock_uom", "valuation_rate"],
                as_dict=True
            )
            
            # If not found locally or it is a standard Item, check remote
            if not item:
                remote_item = get_erpnext_item(item_code)
                if remote_item:
                    item = {
                        "item_name": remote_item.get("item_name"),
                        "description": remote_item.get("description"),
                        "stock_uom": remote_item.get("stock_uom"),
                        "valuation_rate": get_erpnext_item_cost(item_code, self.rm_cost_as_per or "Valuation Rate")
                    }
            
            if not item:
                item = {}

        rate = flt(item.get("valuation_rate"))
        return {
            "item_name": item.get("item_name") or "",
            "description": item.get("description") or "",
            "stock_uom": item.get("stock_uom") or "",
            "uom": item.get("stock_uom") or "",
            "rate": rate,
            "base_rate": rate * flt(self.conversion_rate or 1),
            "qty": flt(args.get("qty") or 1),
            "amount": rate * flt(args.get("qty") or 1),
            "base_amount": rate * flt(self.conversion_rate or 1) * flt(args.get("qty") or 1),
        }

    @frappe.whitelist()
    def calculate_cost(self):
        """Calculates the total cost based on the valuation method."""
        total_cost = 0
        valuation_method = self.rm_cost_as_per or "Valuation Rate"
        frappe.log_error(f"NPD Calculate Cost Method: {valuation_method}, RM Cost As Per: {self.rm_cost_as_per}", "NPD Debug")
        
        for item in self.items:
            rate = 0
            item_type = item.item_doctype
            
            # 1. Try fetching rate based on item type
            if item_type == "Item":
                rate = get_erpnext_item_cost(item.item_code, valuation_method)
                frappe.log_error(f"Fetched Remote Rate for {item.item_code} via {valuation_method}: {rate}", "NPD Debug")
            elif item_type == "NPD Item":
                rate = frappe.db.get_value("NPD Item", item.item_code, "valuation_rate") or 0
            
            # 2. Fallback: If rate is 0, try to check if it's the other type or just trust existing rate
            if not rate and item.rate:
                rate = item.rate
                
            frappe.log_error(f"Calculate Cost Item: {item.item_code}, Type: {item_type}, Rate: {rate}", "NPD Debug")
            
            item.rate = flt(rate)
            item.base_rate = item.rate * flt(self.conversion_rate or 1)
            item.amount = flt(item.qty) * item.rate
            item.base_amount = flt(item.qty) * item.base_rate
            total_cost += item.amount
            
        self.total_cost = flt(total_cost)
        self.base_total_cost = self.total_cost * flt(self.conversion_rate or 1)
        self.raw_material_cost = self.total_cost
        self.base_raw_material_cost = self.base_total_cost
        
        return {
            "items": [{"rate": i.rate, "amount": i.amount, "base_rate": i.base_rate, "base_amount": i.base_amount} for i in self.items],
            "total_cost": self.total_cost,
            "base_total_cost": self.base_total_cost,
            "raw_material_cost": self.raw_material_cost,
            "base_raw_material_cost": self.base_raw_material_cost
        }

    @frappe.whitelist()
    def calculate_nutritional_info(self):
        """Rolls up nutritional information from components, normalized to 100g (0.1kg)."""
        nutritional_fields = [
            "sodio_mg", "fibra_dietetica_g", "azucares_g", "carbohidratos_g",
            "grasas_saturadas_g", "grasas_g", "proteinas_g", "contenido_energetico_kj",
            "contenido_energetico_kcal", "grasas_trans_g", "colesterol_mg",
            "vit_d_ug", "calcio_mg", "hierro_mg", "potasio_mg", "azucares_anadidos_g"
        ]
        
        totals = {field: 0 for field in nutritional_fields}
        total_weight_kg = 0
        
        for item in self.items:
            # 1. Only consider items marked as having nutritional content
            if not getattr(item, "has_nutritional_content", 1):
                continue
                
            item_type = item.item_doctype
            item_data = None
            
            if item_type == "NPD Item":
                item_data = frappe.get_doc("NPD Item", item.item_code)
            else:
                item_data = get_erpnext_item(item.item_code)
            
            if item_data:
                # 2. Determine weight in KG
                qty = flt(item.qty)
                uom = (item.uom or "").lower()
                conv_factor = 1.0
                
                if uom in ["g", "gram", "gramo"]: conv_factor = 0.001
                elif uom in ["mg", "milligram", "miligramo"]: conv_factor = 0.000001
                elif uom in ["lb", "pound", "libra"]: conv_factor = 0.453592
                elif uom in ["oz", "ounce", "onza"]: conv_factor = 0.0283495
                elif uom in ["kg", "kilogram", "kilogramo"]: conv_factor = 1.0
                
                weight_kg = qty * conv_factor
                total_weight_kg += weight_kg
                
                # 3. Calculate nutrients contributed by this row (assuming item master values are per 100g)
                # Formula: Nutrient_Total = (Val_per_100g / 0.1) * Weight_in_KG
                for field in nutritional_fields:
                    val_per_100g = flt(item_data.get(field))
                    nutrient_amount = (val_per_100g / 0.1) * weight_kg
                    totals[field] += nutrient_amount
                    
        # 4. Normalize parent fields to "per 100g"
        # Formula: Parent_Val_per_100g = Total_Nutrient / (Total_Weight_KG / 0.1)
        if total_weight_kg > 0:
            weight_factor = total_weight_kg / 0.1
            for field in nutritional_fields:
                setattr(self, field, totals[field] / weight_factor)
        else:
            for field in nutritional_fields:
                setattr(self, field, 0)

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes the NPD BOM to a real BOM in ERPNext."""
        doc_data = self.as_dict()
        
        # Ensure the parent item exists in ERPNext
        if self.item_doctype == "NPD Item":
            linked_item = frappe.db.get_value("NPD Item", self.item, "linked_item")
            if not linked_item:
                frappe.throw(f"The parent item {self.item} must be promoted to ERPNext before its BOM can be promoted.")
            doc_data["item"] = linked_item
        else:
            doc_data["item"] = self.item

        # Map NPD Item references in child table to ERPNext Item references
        for item in doc_data.get("items", []):
            item_type = item.get("item_doctype")
            if item_type == "NPD Item":
                linked_item = frappe.db.get_value("NPD Item", item["item_code"], "linked_item")
                if not linked_item:
                    frappe.throw(f"Component {item['item_code']} is an NPD Item and must be promoted first.")
                item["item_code"] = linked_item
            
            # Remove NPD-specific child field
            if "item_doctype" in item:
                del item["item_doctype"]
        
        # Clean up parent internal fields
        exclude_fields = ["name", "is_promoted", "linked_item", "doctype", "owner", 
                          "creation", "modified", "modified_by", "item_doctype", "default_item_doctype"]
        for field in exclude_fields:
            if field in doc_data:
                del doc_data[field]
        
        try:
            response = push_to_erpnext("BOM", doc_data)
            if response and response.get("name"):
                self.is_promoted = 1
                self.linked_item = response["name"]
                self.save()
                frappe.msgprint(f"Successfully created BOM {self.linked_item} in ERPNext.")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "NPD BOM Promotion Error")
            frappe.throw(f"Failed to promote BOM: {str(e)}")
