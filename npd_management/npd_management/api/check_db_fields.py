import frappe

def execute():
    # Check DocFields
    docfields = frappe.db.get_list('DocField', filters={'options': 'NPD Nutritional Profile'}, fields=['parent', 'fieldname'])
    for d in docfields:
        print("DocField", d)
    
    # Check Custom Fields
    custom_fields = frappe.db.get_list('Custom Field', filters={'options': 'NPD Nutritional Profile'}, fields=['dt', 'fieldname'])
    for d in custom_fields:
        print("Custom Field", d)
        
    print("Done checking.")
