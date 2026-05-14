import frappe
import json
from npd_management.api.npd_utils import make_api_request

def find_missing_field():
    # 1. Search for ANY Custom Field whose fieldname contains 'hts'
    res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field", 
        "filters": json.dumps([["fieldname", "like", "%hts%"]]),
        "fields": ["dt", "fieldname", "options", "label"]
    })
    print(f"Custom Fields matching 'hts': {res.get('message', [])}")
    
    # 2. Search for ANY Custom Field whose fieldname contains 'codigo'
    res2 = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field", 
        "filters": json.dumps([["fieldname", "like", "%codigo%"]]),
        "fields": ["dt", "fieldname", "options", "label"]
    })
    print(f"Custom Fields matching 'codigo': {res2.get('message', [])}")

if __name__ == "__main__":
    find_missing_field()
