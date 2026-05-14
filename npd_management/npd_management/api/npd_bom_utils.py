"""
NPD BOM Utility Methods
========================
Server-side helpers called by the NPD BOM client scripts.
"""
import frappe


@frappe.whitelist()
def get_item_details(item_code, item_doctype="NPD Item"):
    """
    Fetch relevant item details for the BOM Items table.
    Works for both NPD Items and standard ERPNext Items.
    """
    if not item_code:
        return {}

    fields = ["item_name", "description", "stock_uom", "valuation_rate"]

    if item_doctype == "NPD Item" and frappe.db.exists("NPD Item", item_code):
        doc = frappe.db.get_value(
            "NPD Item", item_code,
            ["item_name", "description", "stock_uom", "valuation_rate"],
            as_dict=True
        )
        return doc or {}

    elif item_doctype == "Item" and frappe.db.exists("Item", item_code):
        doc = frappe.db.get_value(
            "Item", item_code,
            ["item_name", "description", "stock_uom", "valuation_rate"],
            as_dict=True
        )
        return doc or {}

    return {}
