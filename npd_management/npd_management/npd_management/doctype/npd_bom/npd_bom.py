# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from npd_management.api.npd_utils import push_to_erpnext
from npd_management.api.npd_promotion import build_promotion_data, strip_row_meta
from npd_management.utils.nutritional_rollup import (
    apply_rollup_to_doc,
    collect_profile_names_from_items,
    rollup_nutrition,
)


def _local_item_rate(item_code, valuation_method):
    """Fetch item rate from local Item table only."""
    if not item_code or not frappe.db.exists("Item", item_code):
        return 0
    fieldname = "valuation_rate" if valuation_method == "Valuation Rate" else "last_purchase_rate"
    return flt(frappe.db.get_value("Item", item_code, fieldname))


@frappe.whitelist()
def get_bom_material_detail(item_code=None, item_doctype=None, qty=1, conversion_rate=1, args=None):
    """
    Whitelisted module API to fetch material detail for an item in NPD BOM.
    """
    import json
    if not item_code and not args:
        args = frappe.form_dict

    if isinstance(args, str):
        args = json.loads(args)

    if isinstance(args, dict) and "args" in args:
        args = args["args"]

    if isinstance(args, dict):
        item_code = args.get("item_code") or item_code
        item_doctype = args.get("item_doctype") or item_doctype
        qty = args.get("qty") or qty
        conversion_rate = args.get("conversion_rate") or conversion_rate

    item_doctype = item_doctype or "NPD Item"

    if item_doctype == "NPD Item" and item_code and frappe.db.exists("NPD Item", item_code):
        item = frappe.db.get_value(
            "NPD Item", item_code,
            ["item_name", "description", "stock_uom", "valuation_rate"],
            as_dict=True
        ) or {}
    elif item_code and frappe.db.exists("Item", item_code):
        item = frappe.db.get_value(
            "Item", item_code,
            ["item_name", "description", "stock_uom", "valuation_rate"],
            as_dict=True
        ) or {}
    else:
        item = {}

    rate = flt(item.get("valuation_rate"))
    conv = flt(conversion_rate or 1)
    quantity = flt(qty or 1)
    return {
        "item_name": item.get("item_name") or "",
        "description": item.get("description") or "",
        "stock_uom": item.get("stock_uom") or "",
        "uom": item.get("stock_uom") or "",
        "rate": rate,
        "base_rate": rate * conv,
        "qty": quantity,
        "amount": rate * quantity,
        "base_amount": rate * conv * quantity,
    }


@frappe.whitelist()
def check_kg_conversions(items_json=None):
    """Scan BOM items JSON for missing Kg conversions."""
    import json
    if not items_json:
        items_json = frappe.form_dict.get("items_json")
    if isinstance(items_json, str):
        items = json.loads(items_json)
    else:
        items = items_json or []
    from npd_management.utils.nutritional_rollup import check_missing_kg_conversions
    return check_missing_kg_conversions(items, item_doctype_key="item_doctype", default_item_doctype="NPD Item")


@frappe.whitelist()
def save_kg_conversions(conversions=None):
    """Save explicit Kg conversion factors directly into the Item's UOM table."""
    import json
    if not conversions:
        conversions = frappe.form_dict.get("conversions")
    if isinstance(conversions, str):
        conversions_list = json.loads(conversions)
    else:
        conversions_list = conversions or []
    
    for row in conversions_list:
        doc = frappe.get_doc(row.get("item_doctype", "NPD Item"), row.get("item_code"))
        doc.append("uoms", {
            "uom": "Kg",
            "conversion_factor": flt(row.get("conversion_factor"))
        })
        doc.flags.ignore_permissions = True
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.save()
        
    return True


class NPDBOM(Document):
    def validate(self):
        self._ensure_item_doctypes()
        self.calculate_cost()
        self.calculate_nutritional_info()

    def _ensure_item_doctypes(self):
        """Auto-set item_doctype on rows where it is missing, so Dynamic Link validation passes."""
        default_type = getattr(self, "default_item_doctype", None) or "NPD Item"
        for row in getattr(self, "items", []):
            if not row.item_doctype:
                row.item_doctype = default_type

    @frappe.whitelist()
    def get_bom_material_detail(self, args=None):
        return get_bom_material_detail(conversion_rate=self.conversion_rate, args=args)

    @frappe.whitelist()
    def calculate_cost(self):
        """Calculates the total cost based on the valuation method (local DB only)."""
        total_cost = 0
        valuation_method = self.rm_cost_as_per or "Valuation Rate"

        for item in getattr(self, "items", []):
            rate = 0
            item_type = item.item_doctype or getattr(self, "default_item_doctype", "NPD Item")

            if item_type == "Item":
                rate = _local_item_rate(item.item_code, valuation_method)
            elif item_type == "NPD Item":
                rate = frappe.db.get_value("NPD Item", item.item_code, "valuation_rate") or 0

            if not rate and item.rate:
                rate = item.rate

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
            "items": [{"rate": i.rate, "amount": i.amount, "base_rate": i.base_rate, "base_amount": i.base_amount} for i in getattr(self, "items", [])],
            "total_cost": self.total_cost,
            "base_total_cost": self.base_total_cost,
            "raw_material_cost": self.raw_material_cost,
            "base_raw_material_cost": self.base_raw_material_cost
        }

    @frappe.whitelist()
    def calculate_nutritional_info(self):
        """
        Rolls up nutritional information from NPD Nutritional Profile records.
        Result is normalized to npdi_reference_quantity_g on the parent NPD BOM.
        """
        if getattr(self, "nutritional_snapshot_locked", 0):
            return {}

        parent_ref_qty = flt(self.get("npdi_reference_quantity_g") or 100.0)
        totals = rollup_nutrition(getattr(self, "items", []), parent_ref_qty=parent_ref_qty)
        warnings = totals.pop("warnings", [])
        
        apply_rollup_to_doc(self, totals)
        return {"warnings": warnings}

    @frappe.whitelist()
    def check_kg_conversions(self, items_json):
        return check_kg_conversions(items_json)

    @frappe.whitelist()
    def save_kg_conversions(self, conversions):
        return save_kg_conversions(conversions)

    def on_submit(self):
        """
        On NPD BOM submission: lock referenced profiles and freeze the snapshot.
        """
        from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import (
            lock_profile,
        )

        for profile_name in collect_profile_names_from_items(self.items):
            lock_profile(profile_name)

        frappe.db.set_value("NPD BOM", self.name, "nutritional_snapshot_locked", 1)

    @frappe.whitelist()
    @staticmethod
    def get_promotion_data(npd_item_name):
        """
        Returns a clean dict mapped to the standard BOM doctype, suitable for
        frappe.route_options to pre-fill the full BOM form.

        Validates that:
        - The parent item is a promoted NPD Item (has a linked_item).
        - All component NPD Items are promoted.
        Then remaps item codes and strips NPD-specific fields.
        """
        npd_bom = frappe.get_doc("NPD BOM", npd_item_name)
        if npd_bom.is_promoted:
            frappe.throw(f"NPD BOM <b>{npd_item_name}</b> has already been promoted.")

        # Resolve the BOM header item
        if npd_bom.item_doctype == "NPD Item":
            linked_item = frappe.db.get_value("NPD Item", npd_bom.item, "linked_item")
            if not linked_item:
                frappe.throw(
                    f"Parent item <b>{npd_bom.item}</b> must be promoted to an ERPNext Item before its BOM can be promoted."
                )
        else:
            linked_item = npd_bom.item

        from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import NUTRITIONAL_FIELDS
        _BOM_EXCLUDE = {
            "is_promoted", "linked_item", "item_doctype", "default_item_doctype",
            "npdi_reference_quantity_g", "nutrition_facts_section", "nutritional_snapshot_locked",
            "npdi_total_yield_kg"
        }.union(set(NUTRITIONAL_FIELDS))
        data = build_promotion_data(
            npd_bom, "BOM",
            extra_exclude=_BOM_EXCLUDE,
            child_table_fields=["operations", "scrap_items"],
        )

        # Override the item with the real ERPNext item code
        data["item"] = linked_item
        # Mark back-reference for after_insert hook
        data["custom_npd_bom_reference"] = npd_bom.name

        # Remap BOM items child table (items field handled separately for remapping)
        clean_items = []
        for item in npd_bom.get("items", []):
            item_d = item.as_dict()
            item_code = item_d.get("item_code")
            item_type = item_d.get("item_doctype")
            if item_type == "NPD Item":
                linked = frappe.db.get_value("NPD Item", item_code, "linked_item")
                if not linked:
                    frappe.throw(
                        f"Component <b>{item_code}</b> is an NPD Item and must be promoted first."
                    )
                item_code = linked
            row = {k: v for k, v in item_d.items() if k not in {
                "name", "parent", "parentfield", "parenttype", "owner",
                "creation", "modified", "modified_by", "idx", "doctype", "item_doctype",
            }}
            row["item_code"] = item_code
            clean_items.append(row)
        data["items"] = clean_items

        return data

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes the NPD BOM to a real BOM in ERPNext."""
        doc_data = self.as_dict()

        if self.item_doctype == "NPD Item":
            linked_item = frappe.db.get_value("NPD Item", self.item, "linked_item")
            if not linked_item:
                frappe.throw(f"The parent item {self.item} must be promoted to ERPNext before its BOM can be promoted.")
            doc_data["item"] = linked_item
        else:
            doc_data["item"] = self.item

        for item in doc_data.get("items", []):
            item_type = item.get("item_doctype")
            if item_type == "NPD Item":
                linked_item = frappe.db.get_value("NPD Item", item["item_code"], "linked_item")
                if not linked_item:
                    frappe.throw(f"Component {item['item_code']} is an NPD Item and must be promoted first.")
                item["item_code"] = linked_item

            if "item_doctype" in item:
                del item["item_doctype"]

        from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import NUTRITIONAL_FIELDS
        exclude_fields = ["name", "is_promoted", "linked_item", "doctype", "owner",
                          "creation", "modified", "modified_by", "item_doctype", "default_item_doctype",
                          "npdi_reference_quantity_g", "nutrition_facts_section", "nutritional_snapshot_locked",
                          "npdi_total_yield_kg"] + list(NUTRITIONAL_FIELDS)
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


# Expose the static method at the module level for frappe.call route
get_promotion_data = NPDBOM.get_promotion_data
