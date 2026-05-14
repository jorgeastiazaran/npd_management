# -*- coding: utf-8 -*-
import frappe
from frappe.utils import get_url, flt
import requests
import json

def make_api_request(method, endpoint, params=None, data=None):
    """
    Wrapper for making requests to the production ERPNext instance using API Token.
    """
    url = frappe.conf.get("npd_erpnext_url")
    api_key = frappe.conf.get("npd_api_key")
    api_secret = frappe.conf.get("npd_api_secret")
    
    if not url or not api_key or not api_secret:
        frappe.throw("Missing API credentials in site_config.json")
        
    if endpoint.startswith("api/"):
        full_url = f"{url.rstrip('/')}/{endpoint}"
    else:
        full_url = f"{url.rstrip('/')}/api/method/{endpoint}"
    
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Accept": "application/json"
    }
    
    if data:
        data = json.loads(frappe.as_json(data))
        
    response = requests.request(method, full_url, headers=headers, params=params, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_msg = response.text
        try:
            error_json = response.json()
            if "exc" in error_json:
                error_msg = error_json.get("exception", error_json.get("exc"))
            elif "_server_messages" in error_json:
                messages = json.loads(error_json["_server_messages"])
                error_msg = ", ".join([json.loads(m).get("message", "") for m in messages])
        except Exception:
            pass
            
        frappe.log_error(f"Remote API Error: {error_msg}\nURL: {full_url}\nData: {data}", "NPD API Error")
        frappe.throw(f"Remote Server Error: {error_msg}")
        
    return response.json()

def is_remote():
    return bool(frappe.conf.get("npd_erpnext_url"))

def get_erpnext_item(item_code):
    """Fetches Item details from ERPNext via REST API or local database."""
    if not is_remote():
        if frappe.db.exists("Item", item_code):
            return frappe.get_doc("Item", item_code).as_dict()
        return None
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "Item", "name": item_code})
    return res.get("message")

def get_erpnext_item_cost(item_code, method):
    """Fetches Item cost based on Valuation Rate or Last Purchase Rate."""
    if not is_remote():
        fieldname = "valuation_rate" if method == "Valuation Rate" else "last_purchase_rate"
        return flt(frappe.db.get_value("Item", item_code, fieldname))
        
    if method == "Valuation Rate":
        res = make_api_request("GET", "frappe.client.get_value", params={
            "doctype": "Item", 
            "fieldname": "valuation_rate", 
            "filters": item_code
        })
        msg = res.get("message")
        if isinstance(msg, dict):
            return msg.get("valuation_rate") or 0
        return flt(msg) or 0
    elif method == "Last Purchase Rate":
        res = make_api_request("GET", "frappe.client.get_value", params={
            "doctype": "Item", 
            "fieldname": "last_purchase_rate", 
            "filters": item_code
        })
        msg = res.get("message")
        if isinstance(msg, dict):
            return msg.get("last_purchase_rate") or 0
        return flt(msg) or 0
    return 0

def get_erpnext_project(project_id):
    """Fetches Project details from ERPNext via REST API or local database."""
    if not is_remote():
        if frappe.db.exists("Project", project_id):
            return frappe.get_doc("Project", project_id).as_dict()
        return None
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "Project", "name": project_id})
    return res.get("message")

def get_erpnext_quality_inspection_parameter(parameter_id):
    """Fetches Quality Inspection Parameter from ERPNext."""
    if not is_remote():
        if frappe.db.exists("Quality Inspection Parameter", parameter_id):
            return frappe.get_doc("Quality Inspection Parameter", parameter_id).as_dict()
        return None
    res = make_api_request("GET", "frappe.client.get", params={
        "doctype": "Quality Inspection Parameter", 
        "name": parameter_id
    })
    return res.get("message")

def get_erpnext_naming_series(doctype):
    """Fetches Naming Series for a specific DocType."""
    if not is_remote():
        return frappe.get_all("Naming Series", filters={"document_type": doctype}, fields=["name", "current_value"])
    res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Naming Series",
        "filters": {"document_type": doctype},
        "fields": ["name", "current_value"]
    })
    return res.get("message")

def push_to_erpnext(doctype, doc_data):
    """Pushes a new document to the ERPNext instance using standard REST API or local ORM."""
    if not is_remote():
        doc_data["doctype"] = doctype
        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True)
        return doc.as_dict()
        
    res = make_api_request("POST", f"api/resource/{doctype}", data=doc_data)
    return res.get("data")

def link_promoted_item(doc, method=None):
    """Document hook triggered after Item insertion to sync promotion status back to NPD Item."""
    if doc.get("custom_npd_reference"):
        if frappe.db.exists("NPD Item", doc.custom_npd_reference):
            npd_item = frappe.get_doc("NPD Item", doc.custom_npd_reference)
            npd_item.is_promoted = 1
            npd_item.linked_item = doc.name
            if not npd_item.item_code:
                npd_item.item_code = doc.name
            npd_item.save(ignore_permissions=True)
            frappe.logger().info(f"Successfully linked promoted Item {doc.name} back to NPD Item {npd_item.name}")
