import frappe

def execute():
    for dt in ["NPD BOM", "NPD Trial"]:
        meta = frappe.get_meta(dt)
        hidden_count = 0
        total_fields = 0
        for df in meta.fields:
            if df.fieldtype not in ["Section Break", "Column Break", "Tab Break"]:
                total_fields += 1
                if df.hidden:
                    hidden_count += 1
        print(f"{dt}: {hidden_count} hidden out of {total_fields} fields")
