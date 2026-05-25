import frappe

def execute():
    meta_bom = frappe.get_meta("NPD BOM")
    meta_trial = frappe.get_meta("NPD Trial")
    
    print("NPD BOM Fields:", len(meta_bom.fields))
    print("NPD Trial Fields:", len(meta_trial.fields))
    
    for df in meta_bom.fields:
        if df.fieldtype in ["Link", "Dynamic Link"]:
            if df.options and not frappe.db.exists("DocType", df.options) and not df.options == "item_doctype":
                print("BROKEN LINK IN BOM:", df.fieldname, df.options)
                
    for df in meta_trial.fields:
        if df.fieldtype in ["Link", "Dynamic Link"]:
            if df.options and not frappe.db.exists("DocType", df.options) and not df.options == "item_doctype":
                print("BROKEN LINK IN TRIAL:", df.fieldname, df.options)
