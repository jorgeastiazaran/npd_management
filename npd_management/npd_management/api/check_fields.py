import frappe
def execute():
    meta = frappe.get_meta("NPD Item")
    print(f"weight_per_unit: {bool(meta.get_field('weight_per_unit'))}")
    print(f"weight_uom: {bool(meta.get_field('weight_uom'))}")
    print(f"uoms: {bool(meta.get_field('uoms'))}")
