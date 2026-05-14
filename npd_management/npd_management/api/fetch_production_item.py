import json
import frappe
from npd_management.api.npd_utils import make_api_request

def fetch_and_save():
    doctype_name = "Item"
    print(f"Fetching '{doctype_name}' DocType from production...")
    
    try:
        res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": doctype_name})
        doc = res.get("message")
        
        if not doc:
            print("Failed to fetch DocType.")
            return
            
        # Instead of saving to a file in the container, we print it clearly
        print("RESULT_JSON_START")
        print(json.dumps(doc))
        print("RESULT_JSON_END")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
