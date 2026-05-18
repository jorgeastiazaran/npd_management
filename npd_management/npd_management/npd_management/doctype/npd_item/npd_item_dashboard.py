from frappe import _

def get_data():
	return {
		"fieldname": "npd_item",
		"non_standard_fieldnames": {
			"NPD BOM": "item",
			"NPD Trial": "production_item",
			"NPD Quality Inspection": "item_code"
		},
		"transactions": [
			{
				"label": _("Development"),
				"items": ["NPD BOM", "NPD Trial"]
			},
			{
				"label": _("Quality"),
				"items": ["NPD Quality Inspection"]
			}
		]
	}
