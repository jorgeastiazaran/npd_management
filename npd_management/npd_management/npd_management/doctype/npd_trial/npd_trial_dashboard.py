from frappe import _

def get_data():
	return {
		"fieldname": "npd_trial",
		"non_standard_fieldnames": {
			"NPD Quality Inspection": "reference_name"
		},
		"internal_links": {
			"NPD Item": ["production_item", "item"],
			"NPD BOM": ["bom_no"]
		},
		"transactions": [
			{
				"label": _("Related Documents"),
				"items": ["NPD Item", "NPD BOM", "NPD Quality Inspection"]
			}
		]
	}
