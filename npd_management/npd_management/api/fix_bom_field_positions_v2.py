import json
import os

def fix_bom_field_positions_v2():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom/npd_bom.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Remove default_item_doctype
    fields = [f for f in fields if f.get("fieldname") != "default_item_doctype"]
    
    # 2. Find the 'items' table
    items_idx = -1
    for i, f in enumerate(fields):
        if f.get("fieldname") == "items":
            items_idx = i
            break
            
    if items_idx != -1:
        # Insert right before 'items'. 
        # This will make it idx 33 (if section break was 32).
        new_field = {
            "fieldname": "default_item_doctype",
            "fieldtype": "Select",
            "label": "Default Item Type (Table)",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "description": "Changes the Item Type for all rows in the table"
        }
        fields.insert(items_idx, new_field)
    
    # 3. Re-index everything
    for i, f in enumerate(fields):
        f["idx"] = i + 1
        
    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    
    # Check what's at idx 32 and 33
    print(f"Re-indexed. Field at idx 32: {fields[31]['fieldname']}, idx 33: {fields[32]['fieldname']}")

if __name__ == "__main__":
    fix_bom_field_positions_v2()
