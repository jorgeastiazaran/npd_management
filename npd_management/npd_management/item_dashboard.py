from frappe import _

def get_data(data=None):
	if data is None:
		data = {}

	if "non_standard_fieldnames" not in data:
		data["non_standard_fieldnames"] = {}
	data["non_standard_fieldnames"]["Nutritional Profile"] = "reference_name"

	found = False
	if "transactions" not in data:
		data["transactions"] = []
		
	for d in data["transactions"]:
		if d.get("label") == _("Quality"):
			if "Nutritional Profile" not in d.get("items", []):
				d.setdefault("items", []).append("Nutritional Profile")
			found = True
			break

	if not found:
		data["transactions"].append({
			"label": _("Quality"),
			"items": ["Nutritional Profile"]
		})

	return data
