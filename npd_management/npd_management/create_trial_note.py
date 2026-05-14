import frappe

def run():
    frappe.init(site="test.localhost", sites_path="sites")
    frappe.connect()
    if frappe.db.exists("DocType", "NPD Trial Note"):
        print("DocType already exists")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "NPD Trial Note",
        "module": "npd_management",
        "custom": 0,
        "istable": 1,
        "editable_grid": 1,
        "fields": [
            {
                "fieldname": "note",
                "fieldtype": "Text Editor",
                "label": "Note",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "added_by",
                "fieldtype": "Data",
                "label": "Added By",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "added_on",
                "fieldtype": "Datetime",
                "label": "Added On",
                "read_only": 1,
                "in_list_view": 1
            }
        ]
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Successfully created NPD Trial Note DocType")

run()
