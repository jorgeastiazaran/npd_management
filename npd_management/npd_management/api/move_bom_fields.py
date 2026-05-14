import json
import os

def move_bom_header_fields():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom/npd_bom.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Identify fields to move
    move_fieldnames = ["item_doctype", "item"]
    fields_to_move = [f for f in fields if f.get("fieldname") in move_fieldnames]
    
    # Remove them from current positions
    fields = [f for f in fields if f.get("fieldname") not in move_fieldnames]
    
    # 2. Find the index of the 'items' table
    items_idx = -1
    for i, f in enumerate(fields):
        if f.get("fieldname") == "items":
            items_idx = i
            break
            
    if items_idx != -1:
        # Insert them before the items table
        # We might want a section break too if there isn't one
        for f in reversed(fields_to_move):
            fields.insert(items_idx, f)
    else:
        print("Could not find 'items' field")
        return

    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    print("Moved item and item_doctype above the items table in NPD BOM")

if __name__ == "__main__":
    move_bom_header_fields()
