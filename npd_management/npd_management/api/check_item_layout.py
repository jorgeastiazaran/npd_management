import frappe

def check_fields():
    meta = frappe.get_meta("Item")
    fields = sorted(meta.fields, key=lambda x: x.idx)
    
    print(f"{'Idx':<5} | {'Fieldname':<30} | {'Type':<15} | {'Perm':<5} | {'Hidden':<5}")
    print("-" * 70)
    for f in fields:
        if "nutrition" in f.fieldname or "manufacturing" in f.fieldname or "contenido" in f.fieldname:
            print(f"{f.idx:<5} | {f.fieldname:<30} | {f.fieldtype:<15} | {f.permlevel:<5} | {f.hidden:<5}")

if __name__ == "__main__":
    check_fields()
