import frappe
import json
from npd_management.api.npd_utils import make_api_request

def fetch_schemas():
    """Fetch full schemas for Supplier, Supplier Quotation, Supplier Quotation Item, 
       Request for Quotation, Request for Quotation Item, Request for Quotation Supplier"""
    doctypes = [
        "Supplier",
        "Supplier Quotation",
        "Supplier Quotation Item",
        "Request for Quotation",
        "Request for Quotation Item",
        "Request for Quotation Supplier",
    ]
    
    for dt in doctypes:
        res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": dt})
        doc = res.get("message", {})
        # Write to /tmp
        with open(f"/tmp/{dt.lower().replace(' ', '_')}_schema.json", "w") as f:
            json.dump(doc, f, indent=2, default=str)
        print(f"Wrote schema for {dt} ({len(doc.get('fields', []))} fields)")

if __name__ == "__main__":
    fetch_schemas()
