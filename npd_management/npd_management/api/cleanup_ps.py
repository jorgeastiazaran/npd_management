import frappe

def cleanup():
    # Delete all property setters for permlevel with value 0 or ""
    frappe.db.sql("DELETE FROM `tabProperty Setter` WHERE doc_type='Item' AND property='permlevel' AND (value='0' OR value='')")
    frappe.db.commit()
    frappe.clear_cache(doctype='Item')
    print("Cleaned up property setters.")

if __name__ == "__main__":
    cleanup()
