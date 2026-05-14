import frappe
import json

def check_permlevels():
    results = frappe.db.get_all("Property Setter", 
                               filters={"doc_type": "Item", "property": "permlevel"}, 
                               fields=["field_name", "value"])
    print(json.dumps(results, indent=2))
    
    # Also check a few fields in Meta
    meta = frappe.get_meta("Item")
    for f in meta.fields:
        if f.permlevel and not isinstance(f.permlevel, int):
            print(f"ERROR: Field {f.fieldname} has permlevel of type {type(f.permlevel)}: {repr(f.permlevel)}")

if __name__ == "__main__":
    check_permlevels()
