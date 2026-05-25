import frappe

def execute():
    meta = frappe.get_meta("NPD BOM")
    print("--- NPD BOM Fields ---")
    for df in meta.fields:
        if df.fieldtype not in ["Section Break", "Column Break", "Tab Break"]:
            print(f"{df.fieldname} ({df.fieldtype}) - Options: {df.options}")
