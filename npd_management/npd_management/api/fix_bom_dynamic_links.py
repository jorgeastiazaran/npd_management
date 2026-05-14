import json
import os

def update_npd_bom_item_dynamic_link():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom_item/npd_bom_item.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Check if item_doctype already exists
    has_doctype = any(f.get("fieldname") == "item_doctype" for f in fields)
    
    if not has_doctype:
        # Insert item_doctype before item_code
        new_field = {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Type",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "in_list_view": 1,
            "reqd": 1,
            "columns": 2
        }
        # Find item_code index
        idx = 0
        for i, f in enumerate(fields):
            if f.get("fieldname") == "item_code":
                idx = i
                break
        fields.insert(idx, new_field)

    # 2. Update item_code to Dynamic Link
    for f in fields:
        if f.get("fieldname") == "item_code":
            f["fieldtype"] = "Dynamic Link"
            f["options"] = "item_doctype"
            f["label"] = "Item Code"
            f["columns"] = 2

    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    print("Updated NPD BOM Item with Dynamic Link")

def update_npd_bom_main_dynamic_link():
    path = "npd_management/npd_management/npd_management/doctype/npd_bom/npd_bom.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r") as f:
        data = json.load(f)

    fields = data.get("fields", [])
    
    # 1. Add item_doctype before item
    has_doctype = any(f.get("fieldname") == "item_doctype" for f in fields)
    if not has_doctype:
        new_field = {
            "fieldname": "item_doctype",
            "fieldtype": "Select",
            "label": "Item Type",
            "options": "NPD Item\nItem",
            "default": "NPD Item",
            "reqd": 1
        }
        idx = 0
        for i, f in enumerate(fields):
            if f.get("fieldname") == "item":
                idx = i
                break
        fields.insert(idx, new_field)

    # 2. Update item to Dynamic Link
    for f in fields:
        if f.get("fieldname") == "item":
            f["fieldtype"] = "Dynamic Link"
            f["options"] = "item_doctype"

    # 3. Fix Conversion Rate label if needed
    for f in fields:
        if f.get("fieldname") == "conversion_rate":
            f["label"] = "Exchange Rate"
            f["default"] = "1.0"

    data["fields"] = fields
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    print("Updated NPD BOM with Dynamic Link and Exchange Rate label")

if __name__ == "__main__":
    update_npd_bom_item_dynamic_link()
    update_npd_bom_main_dynamic_link()
