import frappe
from npd_management.api.npd_utils import make_api_request

def test_api():
    item_code = "MP-0286"
    res = make_api_request("GET", "frappe.client.get_value", params={
        "doctype": "Item", 
        "fieldname": "valuation_rate", 
        "filters": item_code # Passing name as string is also valid in some versions
    })
    print(f"Res for {item_code}: {res}")
    
    res2 = make_api_request("GET", "frappe.client.get_value", params={
        "doctype": "Item", 
        "fieldname": "valuation_rate", 
        "filters": {"name": item_code}
    })
    print(f"Res2 for {item_code}: {res2}")
