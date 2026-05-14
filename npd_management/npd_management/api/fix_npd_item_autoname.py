import frappe

def apply_naming_series():
    """Apply the NPD-specific naming series prefixes to the NPD Item DocType."""
    # User-created prefixes in the test instance
    npd_options = "NPD-PT-.####\nNPD-MP-.####\nNPD-EMB-.####"

    npd_item = frappe.get_doc("DocType", "NPD Item")

    for field in npd_item.fields:
        if field.fieldname == "naming_series":
            field.options = npd_options
            print(f"Updated naming_series options to:\n{npd_options}")
            break

    npd_item.autoname = "naming_series:"
    npd_item.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.reload_doc("npd_management", "doctype", "npd_item")
    print("Done.")
