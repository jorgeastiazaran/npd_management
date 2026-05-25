import json
import os
import frappe

def patch_doctype(path, new_fields, dynamic_link_field=None):
    with open(path) as f:
        data = json.load(f)
    
    fields = data["fields"]
    existing_fieldnames = {df["fieldname"] for df in fields}
    
    for nf in new_fields:
        if nf["fieldname"] not in existing_fieldnames:
            fields.insert(1, nf)
            
    if dynamic_link_field:
        for df in fields:
            if df["fieldname"] == dynamic_link_field:
                df["fieldtype"] = "Dynamic Link"
                df["options"] = "item_doctype"
                
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        
def execute():
    base = frappe.get_app_path("npd_management", "npd_management", "doctype")
    
    # NPD BOM
    patch_doctype(os.path.join(base, "npd_bom", "npd_bom.json"), [
        {
            "fieldname": "default_item_doctype",
            "fieldtype": "Select",
            "label": "Default Item Doctype",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "reqd": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Doctype",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "reqd": 1
        }
    ], "item")
    
    # NPD BOM Item
    patch_doctype(os.path.join(base, "npd_bom_item", "npd_bom_item.json"), [
        {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Doctype",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "in_list_view": 1
        }
    ], "item_code")
    
    # NPD Trial
    patch_doctype(os.path.join(base, "npd_trial", "npd_trial.json"), [
        {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Doctype",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "reqd": 1
        }
    ], "production_item")
    
    # NPD Trial Item
    patch_doctype(os.path.join(base, "npd_trial_item", "npd_trial_item.json"), [
        {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Doctype",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "in_list_view": 1
        }
    ], "item_code")
    
    print("Patched schemas.")

