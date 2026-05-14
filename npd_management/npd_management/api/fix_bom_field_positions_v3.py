import json
import os

def fix_bom_field_positions_v3():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom/npd_bom.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Remove default_item_doctype
    fields = [f for f in fields if f.get("fieldname") != "default_item_doctype"]
    
    # 2. Find section_break_33
    target_idx = -1
    for i, f in enumerate(fields):
        if f.get("fieldname") == "section_break_33":
            target_idx = i + 1 # Insert AFTER this break
            break
            
    if target_idx != -1:
        new_field = {
            "fieldname": "default_item_doctype",
            "fieldtype": "Select",
            "label": "Default Item Type (Table)",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "description": "Changes the Item Type for all rows in the table"
        }
        fields.insert(target_idx, new_field)
    else:
        # Fallback to items table
        for i, f in enumerate(fields):
            if f.get("fieldname") == "items":
                fields.insert(i, new_field)
                break
    
    # 3. Re-index everything
    for i, f in enumerate(fields):
        f["idx"] = i + 1
        
    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    
    print("Re-positioned default_item_doctype correctly after the section break.")

if __name__ == "__main__":
    fix_bom_field_positions_v3()
