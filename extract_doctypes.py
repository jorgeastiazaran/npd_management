import os
import csv
import json
import re
import hashlib
import requests
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

ERPNEXT_URL = os.getenv("ERPNEXT_URL", "").rstrip('/')
API_KEY = os.getenv("USER_API_KEY")
API_SECRET = os.getenv("USER_API_SECRET")

HEADER_MAP = {
    "field name": "fieldname",
    "fieldname": "fieldname",
    "label": "label",
    "field type": "fieldtype",
    "fieldtype": "fieldtype",
    "mandatory": "reqd",
    "reqd": "reqd",
    "hidden": "hidden",
    "read only": "read_only",
    "read_only": "read_only",
    "options": "options",
    "fetch from": "fetch_from",
    "fetch_from": "fetch_from",
    "depends on": "depends_on",
    "depends_on": "depends_on",
    "description": "description",
    "default": "default",
    "in list view": "in_list_view",
    "in_list_view": "in_list_view",
    "print hide": "print_hide",
    "print_hide": "print_hide",
    "report hide": "report_hide",
    "report_hide": "report_hide",
    "columns": "columns",
    "allow in quick entry": "allow_in_quick_entry",
    "allow_in_quick_entry": "allow_in_quick_entry",
    "bold": "bold",
    "collapsible": "collapsible",
    "permlevel": "permlevel"
}

def to_int(value):
    if value is None or str(value).strip() == '':
        return 0
    val_str = str(value).strip().lower()
    try:
        return int(float(val_str))
    except ValueError:
        return 1 if val_str in ('yes', 'true', '1') else 0

def compile_from_csv(doctype_name, csv_path, new_name):
    """Compiles an offline CSV export over the existing application default JSON skeleton to preserve parent metadata."""
    safe_name = new_name.lower().replace(" ", "_")
    skeleton_path = f"npd_management/npd_management/doctype/{safe_name}/{safe_name}.json"
    
    if not os.path.exists(skeleton_path):
        print(f"[ERROR] Default JSON skeleton not found at {skeleton_path}. Please ensure module default bundle source files exist.")
        return None
        
    with open(skeleton_path, "r") as f:
        skeleton = json.load(f)
        
    old_fields = {f.get("fieldname"): f for f in skeleton.get("fields", []) if f.get("fieldname")}
    
    new_fields = []
    seen_fieldnames = set()
    
    print(f"Parsing offline layout CSV for {new_name} from {csv_path}...")
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Normalise column headers
        reader.fieldnames = [h.lower().strip() for h in reader.fieldnames if h]
        
        for row_idx, row in enumerate(reader, start=1):
            # Clean cells
            cleaned_row = {}
            for k, v in row.items():
                if k:
                    cleaned_row[k.strip()] = v.strip() if isinstance(v, str) else v
                    
            mapped = {}
            for csv_key, doc_key in HEADER_MAP.items():
                if csv_key in cleaned_row:
                    mapped[doc_key] = cleaned_row[csv_key]
                    
            ft = mapped.get("fieldtype", "").strip()
            if not ft:
                ft = "Data"
                
            is_break = ft.lower() in ("section break", "column break", "tab break")
            fn = mapped.get("fieldname", "").strip()
            label = mapped.get("label", "").strip()
            
            if not fn:
                if is_break:
                    # Auto-generate compliant snake_case fieldname for breaks
                    hash_str = hashlib.md5(f"{ft}_{label}_{row_idx}".encode()).hexdigest()[:8]
                    fn = f"{ft.lower().replace(' ', '_')}_{hash_str}"
                else:
                    # Skip empty/invalid custom rows
                    continue
                    
            # Sanitise fieldname
            fn = re.sub(r'[^a-z0-9_]', '_', fn.lower())
            
            # Avoid direct duplicate collisions
            if fn in seen_fieldnames:
                fn = f"{fn}_{row_idx}"
            seen_fieldnames.add(fn)
            
            # Retrieve original skeleton field dict to preserve translatable, unique, search_index, etc.
            base = old_fields.get(fn, {}).copy()
            
            # Conditionally mark as custom only if it is a user modification not native to the standard skeleton
            if fn not in old_fields:
                base["is_custom_field"] = 1
            
            # Apply CSV values
            base["fieldname"] = fn
            base["fieldtype"] = ft
            if label or not base.get("label"):
                base["label"] = label
                
            if "reqd" in mapped: base["reqd"] = to_int(mapped["reqd"])
            if "hidden" in mapped: base["hidden"] = to_int(mapped["hidden"])
            if "read_only" in mapped: base["read_only"] = to_int(mapped["read_only"])
            if "options" in mapped: base["options"] = mapped["options"]
            if "fetch_from" in mapped: base["fetch_from"] = mapped["fetch_from"]
            if "depends_on" in mapped: base["depends_on"] = mapped["depends_on"]
            if "description" in mapped: base["description"] = mapped["description"]
            if "default" in mapped: base["default"] = mapped["default"]
            if "permlevel" in mapped: base["permlevel"] = to_int(mapped["permlevel"])
            if "columns" in mapped: base["columns"] = to_int(mapped["columns"])
            if "in_list_view" in mapped: base["in_list_view"] = to_int(mapped["in_list_view"])
            if "print_hide" in mapped: base["print_hide"] = to_int(mapped["print_hide"])
            if "report_hide" in mapped: base["report_hide"] = to_int(mapped["report_hide"])
            
            new_fields.append(base)
            
    # Additively layer any original skeleton fields that were omitted from the CSV export
    for old_fn, old_f in old_fields.items():
        if old_fn not in seen_fieldnames:
            new_fields.append(old_f)
            
    # Assign strict contiguous idx order
    for idx, f in enumerate(new_fields, start=1):
        f["idx"] = idx
        
    skeleton["fields"] = new_fields
    
    # Save back directly
    with open(skeleton_path, "w") as f:
        json.dump(skeleton, f, indent=4)
        
    print(f"Successfully compiled {new_name} offline layout directly into {skeleton_path}")
    return skeleton

def get_doctype_schema(doctype_name):
    """Fetches the base DocType schema, Custom Fields, and Property Setters to compile a unified meta layout."""
    if not ERPNEXT_URL:
        return None
        
    print(f"Fetching {doctype_name} base schema & customization overlays from {ERPNEXT_URL}...")
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Accept": "application/json"
    }
    
    # 1. Fetch Base DocType
    url = f"{ERPNEXT_URL}/api/resource/DocType/{doctype_name}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch base {doctype_name}. Status Code: {response.status_code}")
        return None
        
    schema_data = response.json().get("data", {})
    fields = schema_data.get("fields", [])
    
    # 2. Fetch Custom Fields Overlay
    cf_url = f"{ERPNEXT_URL}/api/resource/Custom Field"
    cf_params = {
        "filters": json.dumps([["dt", "=", doctype_name]]),
        "fields": json.dumps(["*"]),
        "limit_page_length": 1000
    }
    cf_response = requests.get(cf_url, headers=headers, params=cf_params)
    if cf_response.status_code == 200:
        custom_fields = cf_response.json().get("data", [])
        if custom_fields:
            print(f"  Merged {len(custom_fields)} active Custom Fields into layout.")
            for cf in custom_fields:
                # Filter out explicitly deactivated custom fields
                if cf.get("hidden") == 1:
                    continue
                    
                # Filter out raw internal system metadata keys
                new_field = {k: v for k, v in cf.items() if k not in ["name", "dt", "owner", "creation", "modified", "modified_by", "_user_tags", "_comments", "_assign", "_liked_by"]}
                new_field["is_custom_field"] = 1
                
                # Insert based on insert_after topological directive
                insert_after = cf.get("insert_after")
                inserted = False
                if insert_after:
                    for idx, f in enumerate(fields):
                        if f.get("fieldname") == insert_after:
                            fields.insert(idx + 1, new_field)
                            inserted = True
                            break
                if not inserted:
                    fields.append(new_field)
                    
    # 3. Fetch Property Setters Overlay
    ps_url = f"{ERPNEXT_URL}/api/resource/Property Setter"
    ps_params = {
        "filters": json.dumps([["doc_type", "=", doctype_name]]),
        "fields": json.dumps(["field_name", "property", "value"]),
        "limit_page_length": 1000
    }
    ps_response = requests.get(ps_url, headers=headers, params=ps_params)
    if ps_response.status_code == 200:
        property_setters = ps_response.json().get("data", [])
        if property_setters:
            print(f"  Applied {len(property_setters)} customized Property Setters overrides.")
            for ps in property_setters:
                fname = ps.get("field_name")
                prop = ps.get("property")
                val = ps.get("value")
                
                # Cast integer toggles safely
                if prop in ["hidden", "mandatory", "read_only", "allow_in_quick_entry", "bold", "collapsible", "ignore_user_permissions", "in_list_view", "in_standard_filter", "in_global_search", "no_copy", "print_hide", "report_hide"]:
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        pass
                        
                if fname:
                    if prop == "insert_after" and val:
                        # Dynamically re-order base field position
                        target_field = None
                        for idx, f in enumerate(fields):
                            if f.get("fieldname") == fname:
                                target_field = fields.pop(idx)
                                break
                        if target_field:
                            inserted = False
                            for idx, f in enumerate(fields):
                                if f.get("fieldname") == val:
                                    fields.insert(idx + 1, target_field)
                                    inserted = True
                                    break
                            if not inserted:
                                fields.append(target_field)
                    else:
                        # Apply override directly to targeted field
                        for f in fields:
                            if f.get("fieldname") == fname:
                                f[prop] = val
                                break
                else:
                    # Apply override to parent DocType directly
                    schema_data[prop] = val
                    
    # Ensure sequential index alignment
    for idx, f in enumerate(fields):
        f["idx"] = idx + 1
        
    schema_data["fields"] = fields
    return schema_data

def save_doctype_locally(doctype_name, schema_data, new_name):
    """Modifies the schema and saves it locally in the Frappe app structure."""
    if not schema_data:
        return
        
    # Modify the schema properties for custom app wrapping
    schema_data["name"] = new_name
    schema_data["module"] = "npd_management"
    schema_data["custom"] = 1
    
    # Create standard Frappe app subdirectory structure
    safe_name = new_name.lower().replace(" ", "_")
    base_dir = f"npd_management/npd_management/doctype/{safe_name}"
    os.makedirs(base_dir, exist_ok=True)
    
    # Save optimized JSON output
    file_path = os.path.join(base_dir, f"{safe_name}.json")
    with open(file_path, "w") as f:
        json.dump(schema_data, f, indent=4)
        
    # Ensure pure Python controller stubs exist
    py_path = os.path.join(base_dir, f"{safe_name}.py")
    if not os.path.exists(py_path):
        with open(py_path, "w") as f:
            f.write(f"# -*- coding: utf-8 -*-\nimport frappe\nfrom frappe.model.document import Document\n\nclass {new_name.replace(' ', '')}(Document):\n    pass\n")
            
    print(f"Successfully compiled {new_name} locally at {base_dir}")

def main():
    # If run standalone, execute live sync flow
    if not ERPNEXT_URL or "your-erpnext-instance.com" in ERPNEXT_URL:
        print("Please configure your .env file with live target ERPNext URL and API Administrator credentials.")
        return
        
    doctypes_to_fetch = {
        "Item": "NPD Item",
        "BOM": "NPD BOM",
        "BOM Item": "NPD BOM Item",
        "BOM Scrap Item": "NPD BOM Scrap Item",
        "BOM Operation": "NPD BOM Operation",
        "Work Order": "NPD Trial",
        "Work Order Item": "NPD Trial Item",
        "Work Order Operation": "NPD Trial Operation",
        "Quality Inspection Template": "NPD Quality Inspection Template",
        "Quality Inspection": "NPD Quality Inspection",
        "Quality Inspection Reading": "NPD Quality Inspection Reading"
    }
    
    for original_doctype, new_doctype in doctypes_to_fetch.items():
        schema = get_doctype_schema(original_doctype)
        save_doctype_locally(original_doctype, schema, new_doctype)

if __name__ == "__main__":
    main()
