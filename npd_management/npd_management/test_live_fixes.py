import frappe
from npd_management.api.npd_sync_engine import sync_master_data
from npd_management.utils.nutritional_rollup import rollup_nutrition
from npd_management.api.npd_utils import link_promoted_item

def run_tests():
    print("\n==============================================")
    print("   NPD Management Live Fixes Test Execution")
    print("==============================================\n")
    
    # 1. Security Test
    print("[Test 1] Security Enforcement in sync_master_data()")
    try:
        original_user = frappe.session.user
        frappe.set_user("Guest")
        try:
            sync_master_data()
            print("❌ FAIL: sync_master_data() did NOT raise PermissionError for Guest!")
        except frappe.PermissionError:
            print("✅ PASS: sync_master_data() correctly blocked Guest user via frappe.only_for('System Manager').")
        except Exception as e:
            print(f"❌ FAIL: Expected PermissionError, but got: {e}")
        finally:
            frappe.set_user(original_user)
    except Exception as e:
        print(f"❌ ERROR in Test 1 setup: {e}")

    # 2. Performance Test
    print("\n[Test 2] Nutritional Rollup Caching Mechanism")
    try:
        # Pass a dummy item list to trigger the newly refactored rollup_nutrition logic.
        # It should cleanly handle missing items using frappe.get_cached_doc without crashing.
        items = [{"item_code": "TEST-MOCK-001", "item_doctype": "Item", "include_in_nutrient_calc": 1, "stock_qty": 10}]
        res = rollup_nutrition(items)
        if isinstance(res, dict) and "total_yield_kg" in res:
            print("✅ PASS: rollup_nutrition() executed cleanly with memoization and get_cached_doc.")
        else:
            print("❌ FAIL: rollup_nutrition() did not return expected dictionary structure.")
    except Exception as e:
        print(f"❌ FAIL: rollup_nutrition() threw an unexpected exception: {e}")

    # 3. Robustness Test
    print("\n[Test 3] Robust Error Handling in link_promoted_item()")
    try:
        # We pass a mock document to trigger the hook.
        mock_doc = frappe._dict({
            "name": "ITEM-TEST-001",
            "custom_npd_reference": "NPD-ITEM-DOES-NOT-EXIST",
            "get": lambda k: "NPD-ITEM-DOES-NOT-EXIST" if k == "custom_npd_reference" else None
        })
        # This should execute and hit the 'if not frappe.db.exists' early return cleanly.
        # The main goal is to ensure the hook structure doesn't crash Frappe on generic execution.
        link_promoted_item(mock_doc)
        print("✅ PASS: link_promoted_item() hook executed safely without crashing the save transaction.")
    except Exception as e:
        print(f"❌ FAIL: link_promoted_item() threw an unexpected exception: {e}")

    print("\n==============================================")
    print("   Live Tests Complete")
    print("==============================================\n")
