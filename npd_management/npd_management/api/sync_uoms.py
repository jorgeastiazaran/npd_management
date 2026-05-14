"""
Sync UOMs from Production ERPNext into the test instance.
Run via: bench --site test.localhost execute npd_management.api.sync_uoms.sync_uoms
"""
import frappe
import requests
import os

PROD_URL = os.environ.get("ERPNEXT_URL", "https://tecno.posix.mx/")
API_KEY = os.environ.get("USER_API_KEY", "bae78da7bacbb67")
API_SECRET = os.environ.get("USER_API_SECRET", "3ffa8a859d16328")

def get_production_uoms():
    """Fetch all UOM records from production ERPNext."""
    url = f"{PROD_URL.rstrip('/')}/api/resource/UOM"
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    params = {
        "fields": '["name","uom_name","must_be_whole_number","enabled"]',
        "limit_page_length": 500
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def sync_uoms():
    """Sync all production UOMs into this test site, including case corrections."""
    print("Fetching UOMs from production...")
    prod_uoms = get_production_uoms()
    print(f"Found {len(prod_uoms)} UOMs in production.")

    # Build a lower-case lookup of production UOM names for comparison
    prod_by_lower = {u["name"].lower(): u["name"] for u in prod_uoms}

    # Build a lower-case lookup of existing test UOM names
    test_uoms = frappe.get_all("UOM", pluck="name")
    test_by_lower = {u.lower(): u for u in test_uoms}

    created, renamed, skipped = 0, 0, 0

    for prod_name_lower, prod_name in prod_by_lower.items():
        test_name = test_by_lower.get(prod_name_lower)

        if test_name is None:
            # Doesn't exist at all — create it
            doc = frappe.new_doc("UOM")
            doc.uom_name = prod_name
            doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
            created += 1
            print(f"  + Created: {prod_name}")
        elif test_name != prod_name:
            # Exists but with wrong casing — rename it
            print(f"  ~ Renaming: '{test_name}' → '{prod_name}'")
            frappe.rename_doc("UOM", test_name, prod_name, ignore_permissions=True, force=True)
            renamed += 1
        else:
            skipped += 1

    frappe.db.commit()
    print(f"\nDone. Created: {created}, Renamed (case fix): {renamed}, Already correct: {skipped}")
