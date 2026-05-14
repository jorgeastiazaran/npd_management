import json
import os

def fix_bom_field_positions():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom/npd_bom.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Remove default_item_doctype from wherever it is
    fields = [f for f in fields if f.get("fieldname") != "default_item_doctype"]
    
    # 2. Re-calculate indices based on current order (excluding our field for now)
    # Actually, let's find the target position.
    # User says "row 32". Let's find where idx 32 is.
    
    target_idx = 32
    new_field = {
        "fieldname": "default_item_doctype",
        "fieldtype": "Select",
        "label": "Default Item Type (Table)",
        "options": "NPD Item\nItem",
        "default": "NPD Item",
        "description": "Changes the Item Type for all rows in the table",
        "idx": target_idx
    }
    
    # Insert at the correct position in the list.
    # If the list is 0-indexed, and we want it to be idx 32, 
    # then it should be the 32nd element (index 31).
    fields.insert(target_idx - 1, new_field)
    
    # 3. Update all idx values sequentially
    for i, f in enumerate(fields):
        f["idx"] = i + 1
        
    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    print(f"Fixed field positions. 'default_item_doctype' is now at idx {target_idx}.")

if __name__ == "__main__":
    fix_bom_field_positions()
