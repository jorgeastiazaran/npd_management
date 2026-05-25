import json
import os
import frappe

def fix_image_field(path):
    with open(path) as f:
        data = json.load(f)
    
    if data.get("image_field") == "image":
        if not any(f["fieldname"] == "image" for f in data["fields"]):
            data["image_field"] = ""
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Fixed image_field in {path}")
        else:
            print(f"Image field exists in {path}")
            
def execute():
    base = frappe.get_app_path("npd_management", "npd_management", "doctype")
    fix_image_field(os.path.join(base, "npd_bom", "npd_bom.json"))
    fix_image_field(os.path.join(base, "npd_trial", "npd_trial.json"))
