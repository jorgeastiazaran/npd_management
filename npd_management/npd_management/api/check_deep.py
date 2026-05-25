import frappe

def check_dt(dt):
    meta = frappe.get_meta(dt)
    for df in meta.fields:
        if df.fieldtype in ["Link", "Dynamic Link", "Table", "Table MultiSelect"]:
            options = df.options
            if options and options != "item_doctype" and not frappe.db.exists("DocType", options):
                print(f"[{dt}] {df.fieldname} points to MISSING DOCTYPE: {options}")
        
        if df.fieldtype in ["Table", "Table MultiSelect"] and df.options:
            check_dt(df.options)

def execute():
    check_dt("NPD BOM")
    check_dt("NPD Trial")
    print("Done deep checking.")
