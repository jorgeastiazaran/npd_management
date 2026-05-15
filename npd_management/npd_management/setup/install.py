import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Hook executed after app installation to inject custom fields into standard DocTypes."""
    create_custom_fields(get_custom_fields(), ignore_validate=True)

def get_custom_fields():
    return {
        "Item": [
            {
                "fieldname": "custom_npd_reference",
                "label": "NPD Reference",
                "fieldtype": "Link",
                "options": "NPD Item",
                "insert_after": "item_code",
                "read_only": 1,
                "description": "Reference to the original NPD Item this record was promoted from."
            }
        ]
    }
