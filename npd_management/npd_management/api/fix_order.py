import json
import os
import frappe

def fix_order(path, dynamic_link_fieldname, options_fieldname):
    with open(path) as f:
        data = json.load(f)
    
    fields = data["fields"]
    
    # Extract the fields
    options_field = None
    default_options_field = None
    other_fields = []
    
    for df in fields:
        if df["fieldname"] == options_fieldname:
            options_field = df
        elif df["fieldname"] == "default_item_doctype":
            default_options_field = df
        else:
            other_fields.append(df)
            
    # Now, rebuild the fields array.
    # The options field must appear BEFORE the dynamic link field.
    new_fields = []
    for df in other_fields:
        if df["fieldname"] == dynamic_link_fieldname:
            if default_options_field:
                new_fields.append(default_options_field)
            if options_field:
                new_fields.append(options_field)
        new_fields.append(df)
        
    # Recalculate idx
    for i, df in enumerate(new_fields):
        df["idx"] = i + 1
        
    data["fields"] = new_fields
    
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        
def execute():
    base = frappe.get_app_path("npd_management", "npd_management", "doctype")
    
    # NPD BOM
    fix_order(os.path.join(base, "npd_bom", "npd_bom.json"), "item", "item_doctype")
    # NPD BOM Item
    fix_order(os.path.join(base, "npd_bom_item", "npd_bom_item.json"), "item_code", "item_doctype")
    # NPD Trial
    fix_order(os.path.join(base, "npd_trial", "npd_trial.json"), "production_item", "item_doctype")
    # NPD Trial Item
    fix_order(os.path.join(base, "npd_trial_item", "npd_trial_item.json"), "item_code", "item_doctype")
    
    print("Fixed field order and idx.")
