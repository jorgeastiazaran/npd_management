import frappe
from npd_management.api.npd_utils import make_api_request

def check_remote_item():
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    doc = res.get("message", {})
    fields = [f.get("fieldname") for f in doc.get("fields", []) if "hts" in f.get("fieldname") or "codigo" in f.get("fieldname")]
    print(f"Remote Item fields: {fields}")
    
    # Check custom fields too
    import json
    res_cf = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field", 
        "filters": json.dumps({"dt": "Item"}),
        "fields": json.dumps(["fieldname", "options"])
    })
    cfs = res_cf.get("message", [])
    print(f"Remote Item Custom Fields: {cfs}")

if __name__ == "__main__":
    check_remote_item()
