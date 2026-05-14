import frappe
import json

def inspect_workspace():
    meta = frappe.get_meta("Workspace")
    fields = [f.fieldname for f in meta.fields]
    print(f"Fields in Workspace: {fields}")
    
    # Also check if 'links' is a table
    links_field = meta.get_field("links")
    if links_field:
        print(f"'links' field type: {links_field.fieldtype}")
        if links_field.fieldtype == "Table":
            print(f"'links' options: {links_field.options}")

if __name__ == "__main__":
    inspect_workspace()
