import frappe

def execute():
    for dt in ["NPD BOM Item", "NPD BOM Scrap Item", "NPD BOM Operation", "NPD Trial Item", "NPD Trial Operation"]:
        try:
            meta = frappe.get_meta(dt)
            print(f"--- {dt} ---")
            for df in meta.fields:
                if df.fieldtype in ["Link", "Dynamic Link"]:
                    if df.options and not frappe.db.exists("DocType", df.options) and not df.options == "item_doctype":
                        print("BROKEN LINK:", df.fieldname, df.options)
                for attr in ["depends_on", "mandatory_depends_on", "read_only_depends_on", "fetch_from"]:
                    val = getattr(df, attr, None)
                    if val:
                        print(f"{df.fieldname} has {attr}: {val}")
        except Exception as e:
            print(f"Error for {dt}: {e}")

