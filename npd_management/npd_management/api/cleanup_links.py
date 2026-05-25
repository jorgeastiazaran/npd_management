import frappe

def execute():
    # Clear broken links in NPD Item
    frappe.db.sql("""
        UPDATE `tabNPD Item` 
        SET npdi_default_nutritional_profile = NULL 
        WHERE npdi_default_nutritional_profile IS NOT NULL 
        AND npdi_default_nutritional_profile NOT IN (SELECT name FROM `tabNutritional Profile`)
    """)
    # Clear broken links in Item
    frappe.db.sql("""
        UPDATE `tabItem` 
        SET npdi_default_nutritional_profile = NULL 
        WHERE npdi_default_nutritional_profile IS NOT NULL 
        AND npdi_default_nutritional_profile NOT IN (SELECT name FROM `tabNutritional Profile`)
    """)
    frappe.db.commit()
    print("Cleaned up broken nutritional profile links.")
