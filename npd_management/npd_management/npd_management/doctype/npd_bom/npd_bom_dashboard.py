from frappe import _

def get_data():
	return {
		"fieldname": "bom_no",
		"non_standard_fieldnames": {
			"NPD Trial": "bom_no"
		},
		"internal_links": {
			"NPD Item": ["item"]
		},
		"transactions": [
			{
				"label": _("Related Documents"),
				"items": ["NPD Trial", "NPD Item"]
			}
		]
	}
