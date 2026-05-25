import frappe
import os
import json

def run():
    print("--- Debugging Workspace Sync ---")
    
    # 1. Print Workspace python controller file path
    try:
        import frappe.desk.doctype.workspace.workspace as ws
        print("Workspace controller file:", ws.__file__)
    except Exception as e:
        print("Error importing workspace controller:", e)
        
    # 2. Check if NPD Management workspace json is accessible
    app_path = frappe.get_app_path("npd_management")
    ws_file = os.path.join(app_path, "workspace", "npd_management", "npd_management.json")
    print("Expected workspace file path:", ws_file)
    print("Workspace file exists:", os.path.exists(ws_file))
    
    # 3. Read it if it exists
    if os.path.exists(ws_file):
        try:
            with open(ws_file, "r") as f:
                data = json.load(f)
            print("Loaded JSON. Name:", data.get("name"), "Module:", data.get("module"), "is_standard:", data.get("is_standard"))
        except Exception as e:
            print("Error reading workspace JSON:", e)

    # 4. Check what workspaces are in DB
    workspaces = frappe.get_all("Workspace", fields=["name", "module", "is_standard"])
    print("Workspaces in DB:")
    for w in workspaces:
        if w.module in ["npd_management", "erpnext_npdi_suite"] or "NPD" in w.name:
            print(f"  - Name: {w.name}, Module: {w.module}, Standard: {w.is_standard}")

    # 5. Let's try importing it manually using the standard frappe import method
    # In Frappe, standard docs are loaded/sync'd via make_standard_resources
    # Let's see how make_standard_resources imports it
    print("--- Attempting Manual Import of Workspace ---")
    from frappe.modules.import_file import import_file_by_path
    try:
        import_file_by_path(ws_file, force=True)
        print("import_file_by_path completed.")
        frappe.db.commit()
    except Exception as e:
        print("Error during import_file_by_path:", e)
        import traceback
        traceback.print_exc()

    # 6. Verify if it is in DB now
    exists = frappe.db.exists("Workspace", "NPD Management")
    print("NPD Management Workspace exists in DB after manual import:", exists)
