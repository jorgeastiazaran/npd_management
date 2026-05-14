import frappe
import json
from npd_management.api.npd_utils import make_api_request

def find_docfield():
    # Search for ANY DocField (which is the child table of DocType)
    # This is a bit tricky to query directly via REST API if we don't know the parent.
    # But we can query Custom Field.
    
    # Let's try to get the 'Item' DocType again but print EVERYTHING
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    doc = res.get("message", {})
    all_fieldnames = [f.get("fieldname") for f in doc.get("fields", [])]
    print(f"FULL list of Item fieldnames: {all_fieldnames}")
    
    # Is 'codigo_hts' in there?
    if "codigo_hts" in all_fieldnames:
        print("YES! 'codigo_hts' IS in the standard fields of Item in production.")
    else:
        print("NO! 'codigo_hts' is NOT in the standard fields of Item in production.")

if __name__ == "__main__":
    find_docfield()
