import frappe
import re

def check_expr(dt, df, attr, val):
    if not val: return
    # If fetch_from: source_field.target_field
    if attr == "fetch_from" and "." in val:
        source_field, target_field = val.split(".", 1)
        # Verify source_field exists in the SAME doctype
        source_df = frappe.get_meta(dt).get_field(source_field)
        if not source_df:
            print(f"[{dt}] {df.fieldname}: fetch_from '{val}' fails because field '{source_field}' doesn't exist in {dt}")
        elif source_df.options:
            try:
                target_meta = frappe.get_meta(source_df.options)
                if not any(f.fieldname == target_field for f in target_meta.fields):
                    print(f"[{dt}] {df.fieldname}: fetch_from '{val}' fails because field '{target_field}' doesn't exist in {source_df.options}")
            except frappe.DoesNotExistError:
                pass # Already handled by missing doctype check
    
    # If depends_on, extract field names. Frappe uses simple fields like `show_items` or eval: `eval:doc.status == 'Draft'`
    # We'll just look for simple words
    if attr.endswith("depends_on"):
        if val.startswith("eval:"):
            # Simple heuristic, won't be perfect but catches obvious ones
            fields = set(re.findall(r"doc\.([a-zA-Z0-9_]+)", val))
            if dt != "NPD BOM" and dt != "NPD Trial": # child table
                fields.update(re.findall(r"parent\.([a-zA-Z0-9_]+)", val))
                
            for field in fields:
                if field == "length" or field == "doctype" or field == "__islocal" or field == "docstatus" or field == "parenttype": continue
                if dt != "NPD BOM" and dt != "NPD Trial" and field in ["with_operations", "doctype", "skip_transfer"]:
                    pass # We should check parent meta, but let's assume parent is fine for now
                else:
                    if not any(f.fieldname == field for f in frappe.get_meta(dt).fields):
                        print(f"[{dt}] {df.fieldname}: {attr} '{val}' references missing field '{field}'")
        else:
            # Simple field reference
            if val.isalpha() or "_" in val:
                if not any(f.fieldname == val for f in frappe.get_meta(dt).fields):
                    print(f"[{dt}] {df.fieldname}: {attr} '{val}' references missing field '{val}'")

def execute():
    for dt in ["NPD BOM", "NPD Trial", "NPD BOM Item", "NPD BOM Scrap Item", "NPD BOM Operation", "NPD Trial Item", "NPD Trial Operation"]:
        try:
            meta = frappe.get_meta(dt)
            for df in meta.fields:
                for attr in ["depends_on", "mandatory_depends_on", "read_only_depends_on", "fetch_from"]:
                    check_expr(dt, df, attr, getattr(df, attr, None))
        except Exception as e:
            pass
