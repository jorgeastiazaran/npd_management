import frappe

def execute():
    for dt in ["NPD BOM", "NPD Trial"]:
        meta = frappe.get_meta(dt)
        print(f"--- {dt} ---")
        for df in meta.fields:
            for attr in ["depends_on", "mandatory_depends_on", "read_only_depends_on", "fetch_from"]:
                val = getattr(df, attr, None)
                if val:
                    print(f"{df.fieldname} has {attr}: {val}")

