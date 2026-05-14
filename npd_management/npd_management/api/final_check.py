import frappe

def final_check():
    # Check if any client scripts exist for NPD BOM
    scripts = frappe.get_all("Client Script", filters={"dt": ["in", ["NPD BOM", "NPD BOM Item"]]}, fields=["name", "enabled"])
    print(f"Client Scripts in DB: {scripts}")
    
    # Check DocType metadata
    meta = frappe.get_meta("NPD BOM")
    print(f"NPD BOM custom flag: {meta.custom}")
    
    # Check if item_code field exists in child table
    child_meta = frappe.get_meta("NPD BOM Item")
    item_code_field = [f for f in child_meta.fields if f.fieldname == "item_code"]
    if item_code_field:
        print(f"item_code field found in NPD BOM Item. Parent: {item_code_field[0].parent}")
    else:
        print("item_code field NOT found in NPD BOM Item!")
