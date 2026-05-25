import frappe

def execute():
    # Query DocField table directly to see if the database is out of sync with JSON
    for dt in ["NPD BOM", "NPD Trial", "NPD BOM Item", "NPD BOM Scrap Item", "NPD BOM Operation", "NPD Trial Item", "NPD Trial Operation"]:
        fields = frappe.db.sql("""
            SELECT fieldname, options 
            FROM `tabDocField` 
            WHERE parent = %s AND fieldtype IN ('Link', 'Dynamic Link', 'Table', 'Table MultiSelect')
        """, dt, as_dict=1)
        
        for f in fields:
            options = f.get("options")
            if options and options != "item_doctype" and not frappe.db.exists("DocType", options):
                print(f"DATABASE OUT OF SYNC: [{dt}] {f.fieldname} points to MISSING DOCTYPE {options}")
                
    print("Done checking database.")
