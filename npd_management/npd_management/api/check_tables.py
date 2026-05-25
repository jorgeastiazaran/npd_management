import frappe

def execute():
    for dt in ["NPD BOM", "NPD Trial"]:
        meta = frappe.get_meta(dt)
        for df in meta.fields:
            if df.fieldtype in ["Table", "Table MultiSelect"]:
                if df.options and not frappe.db.exists("DocType", df.options):
                    print(f"BROKEN TABLE IN {dt}:", df.fieldname, df.options)
