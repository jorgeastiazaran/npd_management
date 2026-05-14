import pandas as pd
import json
import frappe
from datetime import datetime

def sync_item_layout():
    import os
    this_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(this_dir, 'item_layout.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 1. Update NPD Item JSON
    npd_json_path = os.path.abspath(os.path.join(this_dir, '..', 'npd_management', 'doctype', 'npd_item', 'npd_item.json'))
    if os.path.exists(npd_json_path):
        with open(npd_json_path) as f:
            npd_data = json.load(f)
        
        new_npd_fields = []
        for i, row in df.iterrows():
            field = {"doctype": "DocField", "idx": i + 1}
            for col in df.columns:
                if col == 'row' or col == 'is_custom_field': continue
                val = row[col]
                
                if col in ['non_negative', 'reqd', 'unique', 'in_list_view', 'in_standard_filter', 
                          'in_global_search', 'in_preview', 'bold', 'no_copy', 'allow_in_quick_entry', 
                          'translatable', 'fetch_if_empty', 'permlevel', 'hidden', 'read_only', 
                          'collapsible', 'allow_bulk_edit', 'ignore_user_permissions', 
                          'allow_on_submit', 'report_hide', 'remember_last_selected_value', 
                          'hide_border', 'ignore_xss_filter', 'in_filter', 'hide_seconds', 
                          'hide_days', 'print_hide', 'print_hide_if_no_value', 'columns', 'precision']:
                    if pd.isna(val) or val == '':
                        val = 0
                    else:
                        try: val = int(float(val))
                        except: val = 0
                elif pd.isna(val) or val == '':
                    continue # Skip empty strings for non-numeric
                
                if col == 'default' and row.get('fieldtype') == 'Date' and val:
                    try:
                        for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                            try:
                                val = datetime.strptime(str(val), fmt).strftime("%Y-%m-%d")
                                break
                            except: continue
                    except: pass
                field[col] = val
            
            # FORCE LEVEL 0 FOR ALL FIELDS TO ENSURE VISIBILITY
            field["permlevel"] = 0
            new_npd_fields.append(field)
            
        npd_data['fields'] = new_npd_fields
        with open(npd_json_path, 'w') as f:
            json.dump(npd_data, f, indent=1)
        print(f"Updated NPD Item JSON with {len(new_npd_fields)} fields.")

    # 2. Update local Item DocType (DB)
    print(f"Syncing {len(df)} fields for Item DocType in database...")
    frappe.db.sql("DELETE FROM `tabProperty Setter` WHERE doc_type='Item'")
    frappe.db.commit()
    
    meta = frappe.get_meta("Item")
    standard_fields_meta = {f.fieldname: f for f in meta.fields if not f.get("is_custom_field")}
    
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter

    for i, row in df.iterrows():
        fieldname = row.get('fieldname')
        if pd.isna(fieldname) or not str(fieldname).strip():
            continue
        
        fieldname = str(fieldname).strip()
        
        props = {}
        for col in df.columns:
            if col in ['row', 'fieldname', 'is_custom_field']: continue
            val = row[col]
            
            # Numeric columns
            if col in ['non_negative', 'reqd', 'unique', 'in_list_view', 'in_standard_filter', 
                        'in_global_search', 'in_preview', 'bold', 'no_copy', 'allow_in_quick_entry', 
                        'translatable', 'fetch_if_empty', 'permlevel', 'hidden', 'read_only', 
                        'collapsible', 'allow_bulk_edit', 'ignore_user_permissions', 
                        'allow_on_submit', 'report_hide', 'remember_last_selected_value', 
                        'hide_border', 'ignore_xss_filter', 'in_filter', 'hide_seconds', 
                        'hide_days', 'print_hide', 'print_hide_if_no_value', 'columns', 'precision']:
                if pd.isna(val) or val == '':
                    val = 0
                else:
                    try: val = int(float(val))
                    except: val = 0
            elif pd.isna(val):
                val = None
            
            # Special handle for Date defaults
            if col == 'default' and row.get('fieldtype') == 'Date' and val:
                try:
                    for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                        try:
                            val = datetime.strptime(str(val), fmt).strftime("%Y-%m-%d")
                            break
                        except: continue
                except: pass
            props[col] = val
        
        props['idx'] = i + 1
        
        # FORCE LEVEL 0 FOR ALL FIELDS
        props["permlevel"] = 0

        try:
            if fieldname in standard_fields_meta:
                field_meta = standard_fields_meta[fieldname]
                for p_name, p_val in props.items():
                    if p_name in ['label', 'fieldtype']: continue
                    current_val = field_meta.get(p_name)
                    if str(current_val) != str(p_val):
                        p_type = "Int" if isinstance(p_val, int) else "Data"
                        if p_name in ['options', 'depends_on', 'description', 'fetch_from']: p_type = "Small Text"
                        try:
                            # Skip if permlevel is 0 (default) to avoid string comparison errors in Frappe
                            if p_name == 'permlevel' and (p_val == 0 or str(p_val) == '0'):
                                continue
                            
                            make_property_setter("Item", fieldname, p_name, str(p_val) if p_val is not None else "", p_type)
                        except Exception: pass # Skip invalid setters
            else:
                cf_dict = {"dt": "Item", "fieldname": fieldname, "is_custom_field": 1}
                cf_dict.update(props)
                valid_fields = [f.fieldname for f in frappe.get_meta("Custom Field").fields]
                final_cf_dict = {k: v for k, v in cf_dict.items() if k in valid_fields or k in ['dt', 'fieldname', 'is_custom_field']}
                
                if frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": fieldname}):
                    cf = frappe.get_doc("Custom Field", {"dt": "Item", "fieldname": fieldname})
                    cf.update(final_cf_dict)
                    cf.save(ignore_permissions=True)
                else:
                    frappe.get_doc({"doctype": "Custom Field", **final_cf_dict}).insert(ignore_permissions=True)
        except Exception: pass

        if i % 20 == 0:
            frappe.db.commit()

    frappe.db.commit()
    frappe.clear_cache(doctype="Item")
    print("Full Sync complete.")
