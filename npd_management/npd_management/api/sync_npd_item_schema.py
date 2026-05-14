import frappe
import json
from npd_management.api.npd_utils import make_api_request


def sync_npd_item_schema():
    """
    Fetches the full Item schema from production (including custom fields)
    and applies it to the local NPD Item DocType so they are identical.
    """
    print("Fetching full Item schema from production...")
    
    # Fetch the DocType definition from production
    res = make_api_request("GET", "frappe.client.get", params={"doctype": "DocType", "name": "Item"})
    item_schema = res.get("message", {})
    
    prod_fields = item_schema.get("fields", [])
    print(f"  Production Item has {len(prod_fields)} standard fields.")
    
    # Fetch custom fields for Item from production
    custom_res = make_api_request("GET", "frappe.client.get_list", params={
        "doctype": "Custom Field",
        "filters": json.dumps([["dt", "=", "Item"]]),
        "fields": json.dumps(["name", "fieldname", "label", "fieldtype", "options", "insert_after",
                              "reqd", "hidden", "read_only", "bold", "in_list_view",
                              "in_standard_filter", "default", "depends_on", "description",
                              "search_index", "unique", "no_copy", "allow_on_submit",
                              "permlevel", "columns", "ignore_xss_filter",
                              "print_hide", "report_hide"]),
        "limit_page_length": 500
    })
    custom_fields = custom_res.get("message", [])
    print(f"  Production Item has {len(custom_fields)} custom fields.")

    # ------------------------------------------------------------------
    # Build the local NPD Item DocType from scratch
    # ------------------------------------------------------------------
    npd_item = frappe.get_doc("DocType", "NPD Item")
    
    # ---- Helper: clean a field dict for insertion into NPD Item ----
    SKIP_KEYS = {"name", "creation", "modified", "modified_by", "owner",
                 "parent", "parenttype", "parentfield", "doctype", "idx",
                 "docstatus", "_seen"}
    LINK_REMAP = {
        # Keep Item-self-references pointing to NPD Item
        "Item": "NPD Item",
    }

    def clean_field(f):
        cleaned = {k: v for k, v in f.items() if k not in SKIP_KEYS}
        # Remap Link options
        if cleaned.get("fieldtype") == "Link":
            opts = cleaned.get("options", "")
            cleaned["options"] = LINK_REMAP.get(opts, opts)
        return cleaned

    # Build ordered field list from standard fields
    new_fields = []
    for f in prod_fields:
        new_fields.append(clean_field(f))

    # Append custom fields AFTER the standard ones (they will be placed
    # via insert_after on the Item form; on NPD Item we just append)
    for cf in custom_fields:
        new_fields.append({
            "fieldname": cf.get("fieldname"),
            "label": cf.get("label"),
            "fieldtype": cf.get("fieldtype"),
            "options": LINK_REMAP.get(cf.get("options", ""), cf.get("options", "")),
            "reqd": cf.get("reqd", 0),
            "hidden": cf.get("hidden", 0),
            "read_only": cf.get("read_only", 0),
            "bold": cf.get("bold", 0),
            "in_list_view": cf.get("in_list_view", 0),
            "in_standard_filter": cf.get("in_standard_filter", 0),
            "default": cf.get("default"),
            "depends_on": cf.get("depends_on"),
            "description": cf.get("description"),
            "search_index": cf.get("search_index", 0),
            "unique": cf.get("unique", 0),
            "no_copy": cf.get("no_copy", 0),
            "print_hide": cf.get("print_hide", 0),
            "report_hide": cf.get("report_hide", 0),
        })

    # Append NPD-specific tracking fields if not already present
    existing_fieldnames = {f.get("fieldname") for f in new_fields}
    npd_extras = [
        {
            "fieldname": "npd_section_break",
            "fieldtype": "Section Break",
            "label": "NPD Status",
        },
        {
            "fieldname": "is_promoted",
            "fieldtype": "Check",
            "label": "Promoted to Item",
            "default": "0",
            "read_only": 1,
        },
        {
            "fieldname": "linked_item",
            "fieldtype": "Link",
            "label": "Linked Item",
            "options": "Item",
            "read_only": 1,
        },
    ]
    for extra in npd_extras:
        if extra["fieldname"] not in existing_fieldnames:
            new_fields.append(extra)

    # ------------------------------------------------------------------
    # Apply to local NPD Item DocType
    # ------------------------------------------------------------------
    # Clear existing fields
    npd_item.fields = []
    for idx, f in enumerate(new_fields, start=1):
        f["idx"] = idx
        npd_item.append("fields", f)

    npd_item.save(ignore_permissions=True)
    frappe.db.commit()

    # Rebuild the DB table
    from frappe.modules.utils import sync_customizations
    frappe.reload_doc("npd_management", "doctype", "npd_item")

    print(f"NPD Item updated with {len(new_fields)} fields (standard + custom + NPD extras).")
    print("Done. Please run: bench --site test.localhost migrate")


if __name__ == "__main__":
    sync_npd_item_schema()
