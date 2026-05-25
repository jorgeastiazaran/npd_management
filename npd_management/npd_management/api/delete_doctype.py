import frappe

def execute():
    frappe.delete_doc("DocType", "NPD Nutritional Profile", force=1, ignore_missing=1)
    frappe.db.commit()
