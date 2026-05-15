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
    skeleton_path = f"npd_management/npd_management/npd_management/doctype/{safe_name}/{safe_name}.json"
    
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
    """Fetches the fully pre-adjudicated compiled DocType schema directly via Frappe's client UI form-loading RPC endpoint."""
    if not ERPNEXT_URL:
        return None
        
    print(f"Fetching {doctype_name} compiled visual layout metadata from {ERPNEXT_URL}...")
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Accept": "application/json"
    }
    
    # Target single pre-adjudicated form meta endpoint directly
    url = f"{ERPNEXT_URL}/api/method/frappe.desk.form.load.getdoctype"
    params = {"doctype": doctype_name}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            print(f"Failed to fetch compiled {doctype_name} meta. Status Code: {response.status_code}")
            return None
        payload = response.json().get("message", {})
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching compiled {doctype_name} meta: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response for {doctype_name}.")
        return None
        
    docs = payload.get("docs", [])
    
    if not docs:
        print(f"Payload docs array empty for {doctype_name}. Verify target API endpoint permissions.")
        return None
        
    # The primary compiled DocType dict is returned first in the docs array
    schema_data = docs[0]
    raw_fields = schema_data.get("fields", [])
    
    print(f"  Successfully extracted {len(raw_fields)} compiled layout fields contiguously.")
    
    system_fields = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "_user_tags", "_comments", "_assign", "_liked_by", "parent", "parenttype", "parentfield", "lft", "rgt", "old_parent"}
    
    cleaned_fields = []
    seen_fn = set()
    
    for f in raw_fields:
        fn = f.get("fieldname")
        # Ensure missing fieldnames or non-customized unlisted hidden core keys are genuinely bypassed
        if not fn or (f.get("hidden") == 1 and not f.get("is_custom_field")):
            continue
            
        # Strip framework internal tracking keys contiguously
        clean_f = {k: v for k, v in f.items() if k not in system_fields}
        
        # Ensure fieldname uniqueness to bypass layout collisions
        if fn in seen_fn:
            continue
        seen_fn.add(fn)
            
        # Secure boolean/integer toggle metrics contiguously
        for prop in ["reqd", "unique", "read_only", "hidden", "in_list_view", "bold", "allow_in_quick_entry", "print_hide", "report_hide"]:
            if prop in clean_f:
                try:
                    clean_f[prop] = int(clean_f[prop])
                except (ValueError, TypeError):
                    clean_f[prop] = 0
                    
        # Avoid non-standard internal structure additions to maintain native compilation schema validity
        clean_f.pop("_t", None)
            
        cleaned_fields.append(clean_f)
        
    # Ensure rigorous contiguous sequence parity mapping
    for idx, f in enumerate(cleaned_fields):
        f["idx"] = idx + 1
        
    # Clean up parent schema doc internals
    for sys_key in system_fields:
        schema_data.pop(sys_key, None)
        
    schema_data["fields"] = cleaned_fields
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
    base_dir = f"npd_management/npd_management/npd_management/doctype/{safe_name}"
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
