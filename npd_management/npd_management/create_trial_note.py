import frappe

def run():
    # Only initialize if not already initialized (e.g. if run outside bench execute)
    if not getattr(frappe.local, "site", None):
        import os
        site = "localhost"
        if os.path.exists("sites/currentsite.txt"):
            with open("sites/currentsite.txt", "r") as f:
                site = f.read().strip()
        frappe.init(site=site, sites_path="sites")
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
