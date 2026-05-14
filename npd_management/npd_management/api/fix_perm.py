import frappe

def fix_perm():
    # Update all fields that contain 'contenido' or 'nutrition' or 'facts'
    fields = frappe.get_all('Custom Field', filters={'dt': 'Item'}, fields=['fieldname'])
    for f in fields:
        if 'nutrition' in f.fieldname or 'facts' in f.fieldname or 'contenido' in f.fieldname or 'kcal' in f.fieldname or 'kj' in f.fieldname:
            print(f"Fixing {f.fieldname}...")
            frappe.db.set_value('Custom Field', {'fieldname': f.fieldname, 'dt': 'Item'}, 'permlevel', 0)
    
    frappe.db.commit()
    frappe.clear_cache(doctype='Item')
    print("Fixed all nutrient fields.")

if __name__ == "__main__":
    fix_perm()
