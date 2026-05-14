import frappe

def cleanup_npd_module():
    # List of DocTypes that SHOULD remain in NPD Management
    npd_doctypes = [
        "NPD Item", "NPD BOM", "NPD Trial", "NPD Quality Inspection",
        "NPD Quality Inspection Template", "NPD Supplier", 
        "NPD Supplier Quotation", "NPD RFQ",
        "NPD BOM Item", "NPD BOM Operation", "NPD BOM Scrap Item",
        "NPD Trial Item", "NPD Trial Operation", "NPD Quality Inspection Reading",
        "NPD Supplier Quotation Item", "NPD RFQ Supplier", "NPD RFQ Item"
    ]
    
    # Find all DocTypes currently in npd_management
    all_docs = frappe.db.get_all("DocType", filters={"module": "npd_management"}, fields=["name"])
    
    for doc in all_docs:
        if doc.name not in npd_doctypes:
            print(f"Removing {doc.name} from NPD Management module...")
            # Move to 'Setup' or keep in their original if possible
            # For now, moving to 'Setup' to hide from NPD view
            frappe.db.set_value("DocType", doc.name, "module", "Setup")
            
    # Also handle specific ones mentioned by user just in case
    specific_removals = ["Company", "Project", "UOM", "Warehouse"]
    for dt in specific_removals:
        if frappe.db.exists("DocType", dt):
            module = frappe.db.get_value("DocType", dt, "module")
            if module == "npd_management":
                 frappe.db.set_value("DocType", dt, "module", "Setup")

    frappe.db.commit()
    print("Module cleanup completed.")

if __name__ == "__main__":
    cleanup_npd_module()
