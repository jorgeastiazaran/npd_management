import frappe

def execute():
    fields = frappe.get_all("Custom Field", filters={"dt": ("in", ["NPD BOM", "NPD Trial", "NPD BOM Item", "NPD BOM Scrap Item", "NPD Trial Item"])}, fields=["name", "dt", "fieldname", "options"])
    for f in fields:
        print(f)
