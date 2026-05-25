import frappe

def execute():
    for dt in ["NPD BOM Item", "NPD BOM Scrap Item", "NPD BOM Operation", "NPD Trial Item", "NPD Trial Operation"]:
        try:
            meta = frappe.get_meta(dt)
            if not meta.istable:
                print(f"ERROR: {dt} is NOT a child table (istable=0)")
        except Exception as e:
            print(f"Error checking {dt}: {e}")
