import frappe

def execute():
    doc = frappe.get_doc("DocType", "Nutritional Profile")
    doc.autoname = "naming_series:"
    doc.is_submittable = 1
    
    # Remove title field
    doc.fields = [f for f in doc.fields if f.fieldname != "title"]
    
    # Check if naming_series exists, if not insert it at the top
    if not any(f.fieldname == "naming_series" for f in doc.fields):
        new_field = frappe._dict({
            "fieldname": "naming_series",
            "fieldtype": "Select",
            "label": "Naming Series",
            "options": "NUTR-.######",
            "reqd": 1,
            "in_list_view": 1,
            "default": "NUTR-.######",
            "set_only_once": 1,
            "print_hide": 1
        })
        doc.append("fields", new_field)
        
        # Move naming_series to index 0
        doc.fields.insert(0, doc.fields.pop())

    # Update permissions for submit, cancel, amend
    for perm in doc.permissions:
        if perm.role == "System Manager":
            perm.submit = 1
            perm.cancel = 1
            perm.amend = 1
            
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Nutritional Profile doctype updated.")
