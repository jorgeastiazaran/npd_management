import json
import requests
import os

# Configuration (reading from .env if needed, but I'll hardcode for speed)
# New Test Instance
URL = "https://tecno13.posix.mx"
API_KEY = "2159cfdb591a269"
API_SECRET = "7c2e286645d9d00"

def make_api_request(method, endpoint, params=None, data=None):
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    url = f"{URL}/api/method/{endpoint}"
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
        
    response.raise_for_status()
    return response.json()

def push_custom_fields():
    with open('project_docs/production_custom_fields.json') as f:
        custom_fields = json.load(f)
        
    print(f"Pushing {len(custom_fields)} custom fields to {URL}...")
    
    for cf in custom_fields:
        fieldname = cf.get('fieldname')
        label = cf.get('label')
        
        doc_data = {
            "doctype": "Custom Field",
            "dt": "Item",
            "fieldname": fieldname,
            "label": label,
            "fieldtype": cf.get("fieldtype"),
            "options": cf.get("options"),
            "insert_after": cf.get("insert_after"),
            "read_only": cf.get("read_only", 0),
            "allow_on_submit": cf.get("allow_on_submit", 0),
            "hidden": cf.get("hidden", 0),
            "reqd": cf.get("reqd", 0),
            "in_list_view": cf.get("in_list_view", 0),
            "permlevel": cf.get("permlevel", 0),
            "precision": cf.get("precision"),
            "depends_on": cf.get("depends_on"),
            "description": cf.get("description"),
            "default": cf.get("default"),
            "in_filter": cf.get("in_filter", 0),
            "no_copy": cf.get("no_copy", 0),
            "print_hide": cf.get("print_hide", 0),
            "report_hide": cf.get("report_hide", 0),
            "unique": cf.get("unique", 0)
        }
        
        try:
            # Check if it exists
            check = make_api_request("GET", "frappe.client.get_list", params={
                "doctype": "Custom Field",
                "filters": json.dumps({"dt": "Item", "fieldname": fieldname}),
                "limit_page_length": 1
            })
            
            if check.get("message"):
                existing_name = check["message"][0]["name"]
                # Update position
                make_api_request("POST", "frappe.client.set_value", data={
                    "doctype": "Custom Field",
                    "name": existing_name,
                    "fieldname": "insert_after",
                    "value": cf.get("insert_after")
                })
            else:
                # Insert
                make_api_request("POST", "frappe.client.insert", data={"doc": doc_data})
        except Exception as e:
            # print(f"Error with {fieldname}: {str(e)}")
            continue
            
    print("Push complete.")

if __name__ == "__main__":
    push_custom_fields()
