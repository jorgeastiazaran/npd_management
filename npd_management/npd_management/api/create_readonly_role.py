import frappe
import json
from npd_management.api.npd_utils import make_api_request

def create_readonly_role():
    role_name = "API read only"
    
    print(f"Checking if role '{role_name}' exists in production...")
    try:
        res = make_api_request("GET", "frappe.client.get", params={"doctype": "Role", "name": role_name})
        print(f"Role '{role_name}' already exists.")
    except Exception:
        print(f"Creating role '{role_name}'...")
        make_api_request("POST", "frappe.client.insert", data={
            "doc": {
                "doctype": "Role",
                "role_name": role_name,
                "disabled": 0
            }
        })

    # Fetching list of all DocTypes
    print("Fetching DocTypes from production...")
    doctypes_res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "DocType",
        "fields": json.dumps(["name"]),
        "filters": json.dumps({"istable": 0, "issingle": 0}),
        "limit_page_length": 1000
    })
    
    doctypes = doctypes_res.get("message", [])
    print(f"Assigning read permissions for {len(doctypes)} DocTypes...")
    
    for dt in doctypes:
        dt_name = dt["name"]
        try:
            make_api_request("POST", "frappe.client.insert", data={
                "doc": {
                    "doctype": "Custom DocPerm",
                    "parent": dt_name,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": role_name,
                    "read": 1,
                    "permlevel": 0
                }
            })
        except Exception:
            continue
            
    print("Permission assignment complete.")

if __name__ == "__main__":
    create_readonly_role()
