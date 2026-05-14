from frappe import _

def get_data():
	return {
		"fieldname": "npd_supplier",
		"non_standard_fieldnames": {
			"NPD Supplier Quotation": "supplier"
		},
		"transactions": [
			{
				"label": _("Procurement"),
				"items": ["NPD Supplier Quotation"]
			}
		]
	}
