import frappe

def execute():
    for dt in ["NPD BOM", "NPD Trial", "NPD BOM Item", "NPD BOM Scrap Item", "NPD BOM Operation", "NPD Trial Item", "NPD Trial Operation"]:
        meta = frappe.get_meta(dt)
        for df in meta.fields:
            if df.fieldtype in ["Link", "Table", "Table MultiSelect"]:
                if not df.options:
                    print(f"[{dt}] {df.fieldname} is a {df.fieldtype} but has NO OPTIONS defined!")
            elif df.fieldtype == "Dynamic Link":
                if not df.options:
                    print(f"[{dt}] {df.fieldname} is a Dynamic Link but has NO OPTIONS defined!")
