import frappe

def check_item_fields():
    item_doc = frappe.get_doc("DocType", "Item")
    fields = [f.fieldname for f in item_doc.fields if "hts" in f.fieldname or "codigo" in f.fieldname]
    print(f"HTS/Codigo fields found in Item: {fields}")
    
    # Check if Codigo HTS exists
    exists = frappe.db.exists("DocType", "Codigo HTS")
    print(f"DocType 'Codigo HTS' exists: {exists}")
    
    # Search for Custom Field locally
    local_cfs = frappe.db.get_all("Custom Field", filters={"fieldname": "codigo_hts"}, fields=["dt", "fieldname", "options"])
    print(f"Local Custom Fields for 'codigo_hts': {local_cfs}")
    
    # Check if CFDI Clave Producto exists
    exists_cfdi = frappe.db.exists("DocType", "CFDI Clave Producto")
    print(f"DocType 'CFDI Clave Producto' exists: {exists_cfdi}")

if __name__ == "__main__":
    check_item_fields()
