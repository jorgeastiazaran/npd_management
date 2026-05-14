import frappe
import json
from npd_management.api.npd_utils import make_api_request

def sync_npd_item_schema_v2():
    """
    Fetches the full Item schema from production and reconstructs the NPD Item DocType
    respecting the exact field order (including sections/columns) from production.
    """
    print("Fetching Item schema and custom fields from production...")
    
    # 1. Get standard fields from DocType
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    item_meta = res.get("message", {})
    standard_fields = item_meta.get("fields", [])
    
    # 2. Get custom fields
    custom_res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field",
        "filters": json.dumps([["dt", "=", "Item"]]),
        "fields": json.dumps(["*"]), # Get all fields
        "limit_page_length": 500
    })
    custom_fields = custom_res.get("message", [])
    
    print(f"  Standard fields: {len(standard_fields)}")
    print(f"  Custom fields: {len(custom_fields)}")

    # 3. Combine fields respecting order
    # Start with standard fields
    final_fields = []
    SKIP_KEYS = {"name", "creation", "modified", "modified_by", "owner",
                 "parent", "parenttype", "parentfield", "doctype", "idx",
                 "docstatus", "_seen"}
    LINK_REMAP = {"Item": "NPD Item"}

    def clean_field(f):
        cleaned = {k: v for k, v in f.items() if k not in SKIP_KEYS}
        if cleaned.get("fieldtype") == "Link":
            opts = cleaned.get("options", "")
            cleaned["options"] = LINK_REMAP.get(opts, opts)
        return cleaned

    for f in standard_fields:
        final_fields.append(clean_field(f))

    # Insert custom fields based on 'insert_after'
    # We use a loop that repeats until all fields are inserted (to handle custom-after-custom)
    pending_fields = custom_fields[:]
    iterations = 0
    while pending_fields and iterations < 10:
        iterations += 1
        new_pending = []
        for cf in pending_fields:
            insert_after = cf.get("insert_after")
            found = False
            for i, f in enumerate(final_fields):
                if f.get("fieldname") == insert_after:
                    final_fields.insert(i + 1, clean_field(cf))
                    found = True
                    break
            if not found:
                new_pending.append(cf)
        pending_fields = new_pending

    # If some are still pending (missing target), just append them
    if pending_fields:
        print(f"  Appending {len(pending_fields)} fields with missing 'insert_after' targets.")
        for cf in pending_fields:
            final_fields.append(clean_field(cf))

    # 4. Add NPD specific fields
    existing_fieldnames = {f.get("fieldname") for f in final_fields}
    npd_extras = [
        {"fieldname": "npd_section_break", "fieldtype": "Section Break", "label": "NPD Status"},
        {"fieldname": "is_promoted", "fieldtype": "Check", "label": "Promoted to Item", "default": "0", "read_only": 1},
        {"fieldname": "linked_item", "fieldtype": "Link", "label": "Linked Item", "options": "Item", "read_only": 1},
    ]
    for extra in npd_extras:
        if extra["fieldname"] not in existing_fieldnames:
            final_fields.append(extra)

    # 5. Apply to NPD Item
    npd_item = frappe.get_doc("DocType", "NPD Item")
    npd_item.fields = []
    for idx, f in enumerate(final_fields, start=1):
        f["idx"] = idx
        npd_item.append("fields", f)

    npd_item.save(ignore_permissions=True)
    frappe.db.commit()

    # Rebuild DB
    frappe.reload_doc("npd_management", "doctype", "npd_item")
    print(f"NPD Item updated. Total fields: {len(final_fields)}")

if __name__ == "__main__":
    sync_npd_item_schema_v2()
