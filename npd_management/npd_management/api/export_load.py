import frappe
from frappe.desk.form.load import getdoctype
import json

def execute():
    try:
        data = getdoctype("NPD BOM")
        with open("/tmp/npd_bom_load.json", "w") as f:
            f.write(frappe.as_json(data))
        print("Exported successfully to /tmp/npd_bom_load.json")
    except Exception as e:
        print("Error exporting:", e)
