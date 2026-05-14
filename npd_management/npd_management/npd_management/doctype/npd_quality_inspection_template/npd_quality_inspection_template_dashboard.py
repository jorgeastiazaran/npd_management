from frappe import _

def get_data():
	return {
		"fieldname": "quality_inspection_template",
		"non_standard_fieldnames": {
			"NPD Quality Inspection": "quality_inspection_template"
		},
		"internal_links": {
			"NPD Item": ["item", "item_code"]
		},
		"transactions": [
			{
				"label": _("Inspections"),
				"items": ["NPD Quality Inspection"]
			},
			{
				"label": _("Related"),
				"items": ["NPD Item"]
			}
		]
	}
