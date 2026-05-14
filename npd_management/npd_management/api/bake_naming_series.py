import json
import os

BASE_PATH = "/Users/jorgeastiazaran/Library/CloudStorage/GoogleDrive-tecnofoodmx@gmail.com/My Drive/PycharmProjects/npd_erpnext/npd_management/npd_management/npd_management/doctype"

def update_json(doctype_name, autoname, ns_options):
    file_path = os.path.join(BASE_PATH, doctype_name.lower().replace(" ", "_"), f"{doctype_name.lower().replace(' ', '_')}.json")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, "r") as f:
        data = json.load(f)
    
    data["autoname"] = autoname
    
    # Update or add naming_series field
    found = False
    for field in data.get("fields", []):
        if field.get("fieldname") == "naming_series":
            field["options"] = ns_options
            field["reqd"] = 1
            found = True
            break
            
    if not found:
        # Add naming_series field at the beginning
        new_field = {
            "fieldname": "naming_series",
            "fieldtype": "Select",
            "label": "Series",
            "options": ns_options,
            "reqd": 1,
            "set_only_once": 1
        }
        data["fields"].insert(0, new_field)
        
    with open(file_path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=False)
    print(f"Updated {doctype_name}")

if __name__ == "__main__":
    # NPD Item
    update_json("NPD Item", "naming_series:", "NPD-PT-.####\nNPD-MP-.####\nNPD-EMB-.####")
    
    # NPD Supplier Quotation
    update_json("NPD Supplier Quotation", "naming_series:", "NPD-SQ-.YYYY.-")
    
    # NPD BOM
    update_json("NPD BOM", "naming_series:", "NPD-BOM-.YYYY.-")
    
    # NPD Trial
    update_json("NPD Trial", "naming_series:", "NPD-TR-.YYYY.-")
    
    # NPD Quality Inspection
    update_json("NPD Quality Inspection", "naming_series:", "NPD-QI-.YYYY.-")
    
    # NPD RFQ is already fine, but let's ensure consistency
    update_json("NPD RFQ", "naming_series:", "NPD-RFQ-.YYYY.-")
