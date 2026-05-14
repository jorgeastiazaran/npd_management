# -*- coding: utf-8 -*-
import frappe
import time
from npd_management.api.npd_utils import make_api_request

@frappe.whitelist()
def sync_master_data():
    """Recursively resolves and syncs all dependencies for core NPD doctypes."""
    # Starting points
    seeds = [
        "Item", "BOM", "Warehouse", "UOM", "Company", "Project", 
        "CFDI Clave Producto", "CFDI Clave Unidad", "Link Type Table"
    ]
    
    # 1. Recursive Metadata Sync (DocTypes, Custom Fields, Property Setters)
    synced_meta = set()
    queue = list(seeds)
    
    while queue:
        dt = queue.pop(0)
        if dt in synced_meta: continue
        
        print(f"Analyzing dependencies for {dt}...")
        # Force fetch schema even if it exists locally for core seeds to capture production fields
        force_fetch = dt in seeds
        deps = sync_meta_and_get_deps(dt, force_fetch=force_fetch)
        synced_meta.add(dt)
        
        for dep in deps:
            if dep not in synced_meta and dep not in queue:
                queue.append(dep)
                
    # 2. Sync Master Data Records (limited to avoid huge pulls)
    summary = [f"Metadata sync complete for: {', '.join(synced_meta)}"]
    for dt in seeds + ["Product Label", "CFDI Clave Producto"]:
        if frappe.db.exists("DocType", dt):
            count = sync_doctype_records(dt)
            summary.append(f"{dt}: {count} records synced")
        
    return "\n".join(summary)

def sync_meta_and_get_deps(doctype, force_fetch=False):
    """Syncs schema/custom fields for a doctype and returns its linked doctypes."""
    deps = set()
    
    # A. Ensure DocType exists locally or force update from remote
    if not frappe.db.exists("DocType", doctype) or force_fetch:
        try:
            doc_res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": doctype})
            doc_data = doc_res.get("message", {})
            
            # Clean and insert/update DocType schema
            for f in ["owner", "creation", "modified", "modified_by", "permissions", "image"]: 
                doc_data.pop(f, None)
            
            doc_data["custom"] = 1
            doc_data["module"] = "npd_management"
            
            if frappe.db.exists("DocType", doctype):
                local_doc = frappe.get_doc("DocType", doctype)
                local_doc.update(doc_data)
                local_doc.save(ignore_permissions=True)
                print(f"  - Updated DocType schema: {doctype}")
            else:
                frappe.get_doc(doc_data).insert(ignore_if_duplicate=True)
                print(f"  - Synced DocType schema: {doctype}")
        except Exception as e:
            print(f"  - Could not fetch schema for {doctype}: {str(e)}")
            return []

    # B. Sync Custom Fields for this DocType
    sync_doctype_records("Custom Field", filters={"dt": doctype})
    
    # C. Sync Property Setters for this DocType
    sync_doctype_records("Property Setter", filters={"doc_type": doctype})

    # D. Identify dependencies (Link and Table fields)
    # Check standard fields
    local_doc = frappe.get_doc("DocType", doctype)
    for field in local_doc.fields:
        if field.fieldtype in ["Link", "Table", "Table MultiSelect"] and field.options:
            dep_dt = field.options
            if not frappe.db.exists("DocType", dep_dt):
                deps.add(dep_dt)
                
    # Check custom fields too!
    custom_fields = frappe.db.get_all("Custom Field", filters={"dt": doctype}, fields=["fieldtype", "options"])
    for field in custom_fields:
        if field.fieldtype in ["Link", "Table", "Table MultiSelect"] and field.options:
            dep_dt = field.options
            if not frappe.db.exists("DocType", dep_dt):
                deps.add(dep_dt)
                
    return list(deps)

def sync_doctype_records(doctype, filters=None):
    """Fetches full document data for all records of a doctype and mirrors them locally."""
    try:
        # 1. Fetch names from remote
        params = {
            "doctype": doctype,
            "limit_page_length": 500
        }
        if filters:
            params["filters"] = frappe.as_json(filters)
            
        res = make_api_request("GET", "frappe.client.get_list", params=params)
        
        remote_records = res.get("message", [])
        synced = 0
        
        for rec in remote_records:
            name = rec.get("name")
            if not frappe.db.exists(doctype, name):
                # 2. Fetch full doc
                doc_res = make_api_request("GET", "frappe.client.get", params={
                    "doctype": doctype,
                    "name": name
                })
                full_doc = doc_res.get("message", {})
                
                # 3. Clean up metadata to allow local insertion
                for field in ["owner", "creation", "modified", "modified_by", "idx", "docstatus"]:
                    full_doc.pop(field, None)
                
                # 4. Insert locally
                try:
                    new_doc = frappe.get_doc(full_doc)
                    new_doc.flags.ignore_permissions = True
                    new_doc.flags.ignore_mandatory = True
                    new_doc.flags.ignore_links = True # Skip deep validation of linked docs we haven't synced yet
                    new_doc.flags.ignore_validate = True
                    new_doc.insert(ignore_if_duplicate=True)
                    print(f"Synced {doctype} {name}")
                    synced += 1
                    time.sleep(0.2) # Small delay to prevent rate limiting
                except Exception as e:
                    frappe.log_error(f"Sync failed for {doctype} {name}", str(e))
        
        frappe.db.commit()
        return synced
    except Exception as e:
        frappe.log_error(f"Sync loop failed for {doctype}", str(e))
        return 0
