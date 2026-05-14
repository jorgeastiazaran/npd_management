import frappe
import json
from npd_management.api.npd_utils import make_api_request

def sync_npd_item_schema_v3():
    """
    Final refinement for NPD Item schema sync:
    - Fetches all standard fields and custom fields.
    - Uses a topological sort approach to respect 'insert_after' order.
    - Specifically ensures Nutritional Info and Logistics sections are placed correctly.
    """
    print("Syncing NPD Item schema (v3)...")
    
    # 1. Get metadata from production
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    item_meta = res.get("message", {})
    standard_fields = item_meta.get("fields", [])
    
    custom_res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field",
        "filters": json.dumps([["dt", "=", "Item"]]),
        "fields": json.dumps(["*"]),
        "limit_page_length": 500
    })
    custom_fields = custom_res.get("message", [])
    
    # 2. Prepare clean field mapping
    SKIP_KEYS = {"name", "creation", "modified", "modified_by", "owner",
                 "parent", "parenttype", "parentfield", "doctype", "idx",
                 "docstatus", "_seen"}
    LINK_REMAP = {"Item": "NPD Item"}

    def clean_field(f):
        cleaned = {k: v for k, v in f.items() if k not in SKIP_KEYS}
        if cleaned.get("fieldtype") == "Link":
            opts = cleaned.get("options", "")
            cleaned["options"] = LINK_REMAP.get(opts, opts)
        # NPD-specific overrides (survive every re-sync)
        if cleaned.get("fieldname") == "naming_series":
            cleaned["options"] = "NPD-PT-.####\nNPD-MP-.####\nNPD-EMB-.####"
            cleaned["reqd"] = 1
        if cleaned.get("fieldname") == "item_code":
            # Hidden and non-mandatory to avoid any UI/Server blocks
            cleaned["unique"] = 1
            cleaned["hidden"] = 1
            cleaned["reqd"] = 0 
            cleaned["no_copy"] = 1
        return cleaned

    # 3. Build the fields list
    # We start with the standard fields as the base order
    final_fields = [clean_field(f) for f in standard_fields]
    
    # Track fieldnames for quick lookup
    fieldnames = [f["fieldname"] for f in final_fields]
    
    # Insert custom fields
    pending = custom_fields[:]
    iterations = 0
    while pending and iterations < 20:
        iterations += 1
        new_pending = []
        for cf in pending:
            target = cf.get("insert_after")
            if not target:
                # If no target, just append or put at start
                final_fields.append(clean_field(cf))
                fieldnames.append(cf["fieldname"])
                continue
                
            if target in fieldnames:
                idx = fieldnames.index(target)
                final_fields.insert(idx + 1, clean_field(cf))
                fieldnames.insert(idx + 1, cf["fieldname"])
            else:
                new_pending.append(cf)
        pending = new_pending

    if pending:
        print(f"  Warning: {len(pending)} fields could not find their 'insert_after' target. Appending to end.")
        for cf in pending:
            final_fields.append(clean_field(cf))
            fieldnames.append(cf["fieldname"])

    # 4. Enforce NPD Status fields at the very end
    npd_extras = [
        {"fieldname": "npd_section_break", "fieldtype": "Section Break", "label": "NPD Status"},
        {"fieldname": "is_promoted", "fieldtype": "Check", "label": "Promoted to Item", "default": "0", "read_only": 1},
        {"fieldname": "linked_item", "fieldtype": "Link", "label": "Linked Item", "options": "Item", "read_only": 1},
    ]
    for extra in npd_extras:
        if extra["fieldname"] not in fieldnames:
            final_fields.append(extra)

    # 5. Save to DocType
    npd_item = frappe.get_doc("DocType", "NPD Item")
    npd_item.autoname = "naming_series:"
    npd_item.fields = []
    for idx, f in enumerate(final_fields, start=1):
        f["idx"] = idx
        npd_item.append("fields", f)

    npd_item.save(ignore_permissions=True)
    frappe.db.commit()
    
    # Reload so it takes effect
    frappe.reload_doc("npd_management", "doctype", "npd_item")
    print(f"Success. Total fields in NPD Item: {len(final_fields)}")

if __name__ == "__main__":
    sync_npd_item_schema_v3()
