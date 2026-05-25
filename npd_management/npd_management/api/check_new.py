import frappe

def execute():
    try:
        doc = frappe.new_doc("NPD BOM")
        print("Created new NPD BOM successfully:", doc.name)
    except Exception as e:
        print("Error creating NPD BOM:", e)
        
    try:
        doc2 = frappe.new_doc("NPD Trial")
        print("Created new NPD Trial successfully:", doc2.name)
    except Exception as e:
        print("Error creating NPD Trial:", e)
