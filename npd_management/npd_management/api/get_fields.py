import frappe

def get_fields():
    print([f.fieldname for f in frappe.get_meta('Error Log').fields])
