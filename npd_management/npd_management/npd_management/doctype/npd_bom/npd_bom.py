# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from npd_management.api.npd_utils import push_to_erpnext
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

        if "args" in args:
            args = args["args"]

        item_code = args.get("item_code")
        item_doctype = args.get("item_doctype") or "NPD Item"

        if item_doctype == "NPD Item" and frappe.db.exists("NPD Item", item_code):
            item = frappe.db.get_value(
                "NPD Item", item_code,
                ["item_name", "description", "stock_uom", "valuation_rate"],
                as_dict=True
            ) or {}
        elif frappe.db.exists("Item", item_code):
            item = frappe.db.get_value(
                "Item", item_code,
                ["item_name", "description", "stock_uom", "valuation_rate"],
                as_dict=True
            ) or {}
        else:
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
        """Calculates the total cost based on the valuation method (local DB only)."""
        total_cost = 0
        valuation_method = self.rm_cost_as_per or "Valuation Rate"

        for item in self.items:
            rate = 0
            item_type = item.item_doctype

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
            "items": [{"rate": i.rate, "amount": i.amount, "base_rate": i.base_rate, "base_amount": i.base_amount} for i in self.items],
            "total_cost": self.total_cost,
            "base_total_cost": self.base_total_cost,
            "raw_material_cost": self.raw_material_cost,
            "base_raw_material_cost": self.base_raw_material_cost
        }

    @frappe.whitelist()
    def calculate_nutritional_info(self):
        """
        Rolls up nutritional information from NPD Nutritional Profile records.
        Result is normalized to 100g on the parent NPD BOM.
        """
        if getattr(self, "nutritional_snapshot_locked", 0):
            return

        totals = rollup_nutrition(self.items)
        apply_rollup_to_doc(self, totals)

    def on_submit(self):
        """
        On NPD BOM submission: lock referenced profiles and freeze the snapshot.
        """
        from npd_management.npd_management.doctype.npd_nutritional_profile.npd_nutritional_profile import (
            lock_profile,
        )

        for profile_name in collect_profile_names_from_items(self.items):
            lock_profile(profile_name)

        frappe.db.set_value("NPD BOM", self.name, "nutritional_snapshot_locked", 1)

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
