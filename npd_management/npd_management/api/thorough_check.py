import frappe
import json
from npd_management.api.npd_utils import make_api_request

def thorough_check():
    # 1. Get ALL Item fieldnames from production
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    doc = res.get("message", {})
    all_fields = [f.get("fieldname") for f in doc.get("fields", [])]
    print(f"Production Item fieldnames: {all_fields}")
    
    # 2. Specifically look for anything similar to 'hts' or 'codigo'
    matches = [f for f in all_fields if "hts" in f or "codigo" in f]
    print(f"Potential matches in standard fields: {matches}")
    
    # 3. Check if 'Codigo HTS' DocType exists via GET (more reliable than get_list)
    try:
        res_hts = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Codigo HTS"})
        print("DocType 'Codigo HTS' EXISTS in production!")
    except:
        print("DocType 'Codigo HTS' NOT FOUND in production via direct GET.")

if __name__ == "__main__":
    thorough_check()
