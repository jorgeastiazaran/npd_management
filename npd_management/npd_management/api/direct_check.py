import frappe
from npd_management.api.npd_utils import make_api_request

def direct_check():
    # Try to GET the specific custom field record
    try:
        res = make_api_request("GET", "frappe.client.get", params={
            "doctype": "Custom Field",
            "name": "Item-codigo_hts"
        })
        print("Custom Field 'Item-codigo_hts' EXISTS in production!")
        print(f"Data: {res.get('message', {})}")
    except:
        print("Custom Field 'Item-codigo_hts' NOT FOUND in production via direct GET.")

if __name__ == "__main__":
    direct_check()
