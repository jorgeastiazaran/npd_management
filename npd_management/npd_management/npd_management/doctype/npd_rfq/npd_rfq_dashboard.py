from frappe import _

def get_data():
	return {
		"fieldname": "npd_rfq",
		"non_standard_fieldnames": {
			"NPD Supplier Quotation": "npd_rfq" # or rfq
		},
		"transactions": [
			{
				"label": _("Quotations"),
				"items": ["NPD Supplier Quotation"]
			}
		]
	}
