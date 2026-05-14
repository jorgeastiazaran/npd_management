import json
import frappe
from npd_management.api.npd_utils import make_api_request

def fetch_custom_fields():
    print("Fetching Custom Fields for 'Item' from production...")
    try:
        res = make_api_request("GET", "frappe.client.get_list", params={
            "doctype": "Custom Field",
            "filters": json.dumps({"dt": "Item"}),
            "fields": json.dumps(["fieldname", "insert_after", "idx", "label", "fieldtype"]),
            "limit_page_length": 500
        })
        custom_fields = res.get("message", [])
        print("RESULT_CUSTOM_FIELDS_START")
        print(json.dumps(custom_fields))
        print("RESULT_CUSTOM_FIELDS_END")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fetch_custom_fields()
