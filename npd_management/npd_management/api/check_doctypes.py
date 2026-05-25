import frappe
import json
import os

def execute():
    missing = []
    base_path = frappe.get_app_path("npd_management", "npd_management", "doctype")
    
    for dt in ["npd_bom", "npd_trial", "npd_bom_item", "npd_bom_scrap_item", "npd_bom_operation", "npd_trial_item", "npd_trial_operation", "bom_explosion_item"]:
        path = os.path.join(base_path, dt, f"{dt}.json")
        if not os.path.exists(path):
            print(f"File {path} not found")
            continue
        with open(path) as f:
            data = json.load(f)
        for field in data["fields"]:
            if field.get("fieldtype") in ["Link", "Table", "Table MultiSelect", "Dynamic Link"]:
                options = field.get("options")
                if options and not frappe.db.exists("DocType", options):
                    print(f"MISSING DOCTYPE: {options} in {dt}.{field.get('fieldname')}")
                    missing.append(options)
                    
    if not missing:
        print("All linked doctypes exist.")
