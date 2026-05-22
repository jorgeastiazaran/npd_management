from frappe import _

def get_data():
    return {
        "fieldname": "npd_item",
        "transactions": [
            {
                "label": _("Nutritional"),
                "items": ["NPD Nutritional Profile"]
            }
        ]
    }
