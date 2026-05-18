from frappe import _

def get_data():
	return {
		"fieldname": "npd_quality_inspection",
		"internal_links": {
			"NPD Item": ["item", "item_code", "production_item"],
			"NPD Trial": ["npd_trial", "reference_name"]
		},
		"transactions": [
			{
				"label": _("Related Documents"),
				"items": ["NPD Item", "NPD Trial"]
			}
		]
	}
