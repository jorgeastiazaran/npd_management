import frappe
import json
from npd_management.api.npd_utils import make_api_request

def find_global_field():
    res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field", 
        "filters": json.dumps({"fieldname": "codigo_hts"}),
        "fields": ["dt", "fieldname", "options"]
    })
    print(f"Global search for 'codigo_hts': {res.get('message', [])}")
    
    # Also check if Codigo HTS is a DocType itself
    res_dt = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "DocType",
        "filters": json.dumps({"name": "Codigo HTS"})
    })
    print(f"Search for 'Codigo HTS' DocType: {res_dt.get('message', [])}")

if __name__ == "__main__":
    find_global_field()
