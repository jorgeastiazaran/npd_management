import frappe

def execute():
    meta = frappe.get_meta("NPD Item")
    print("has_serial_no:", any(df.fieldname == "has_serial_no" for df in meta.fields))
    print("has_batch_no:", any(df.fieldname == "has_batch_no" for df in meta.fields))
