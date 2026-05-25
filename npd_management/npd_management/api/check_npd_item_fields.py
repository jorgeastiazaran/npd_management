import frappe

def execute():
    meta = frappe.get_meta("NPD Item")
    print("has_variants:", any(df.fieldname == "has_variants" for df in meta.fields))
    print("include_item_in_manufacturing:", any(df.fieldname == "include_item_in_manufacturing" for df in meta.fields))
