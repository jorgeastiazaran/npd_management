# -*- coding: utf-8 -*-
"""Verification script for npd_management codebase fixes."""
import frappe
from frappe.utils import flt
import unittest
import json

class TestNpdManagementFixes(unittest.TestCase):
    def setUp(self):
        frappe.init(site="localhost", sites_path="/home/frappe/frappe-bench/sites")
        frappe.connect()
        frappe.set_user("Administrator")
        
        # Ensure we have the test non-permission user
        if not frappe.db.exists("User", "no-permission-test@example.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "no-permission-test@example.com",
                "first_name": "No Perm",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            
        # Ensure we have a test Item
        if not frappe.db.exists("Item", "TEST-FIX-ITEM-1"):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-FIX-ITEM-1",
                "item_name": "Test Fix Item 1",
                "item_group": "All Item Groups",
                "stock_uom": "Gram",
                "is_stock_item": 1
            })
            doc.insert(ignore_permissions=True)
            
    def tearDown(self):
        frappe.set_user("Administrator")
        # Clean up UOM conversions added to TEST-FIX-ITEM-1
        if frappe.db.exists("Item", "TEST-FIX-ITEM-1"):
            doc = frappe.get_doc("Item", "TEST-FIX-ITEM-1")
            doc.uoms = [u for u in doc.uoms if u.uom.lower() != "kg"]
            doc.save(ignore_permissions=True)
        frappe.db.commit()

    def test_save_kg_conversions_type_restriction(self):
        """Verify that save_kg_conversions throws an error on non-whitelisted doctypes."""
        from npd_management.bom_nutrition import save_kg_conversions
        payload = json.dumps([{
            "item_doctype": "User",
            "item_code": "Administrator",
            "conversion_factor": 10
        }])
        
        with self.assertRaises(frappe.ValidationError):
            save_kg_conversions(payload)

    def test_save_kg_conversions_permission_enforcement(self):
        """Verify that save_kg_conversions enforces write permissions."""
        from npd_management.bom_nutrition import save_kg_conversions
        payload = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1",
            "conversion_factor": 1000.0
        }])
        
        # Switch to unauthorized user
        frappe.set_user("no-permission-test@example.com")
        try:
            with self.assertRaises(frappe.ValidationError):
                save_kg_conversions(payload)
        finally:
            frappe.set_user("Administrator")

    def test_save_kg_conversions_factor_validation(self):
        """Verify that save_kg_conversions throws validation error for zero/negative factors."""
        from npd_management.bom_nutrition import save_kg_conversions
        payload_zero = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1",
            "conversion_factor": 0
        }])
        payload_negative = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1",
            "conversion_factor": -5
        }])
        
        with self.assertRaises(frappe.ValidationError):
            save_kg_conversions(payload_zero)
            
        with self.assertRaises(frappe.ValidationError):
            save_kg_conversions(payload_negative)

    def test_save_kg_conversions_upsert_duplicates(self):
        """Verify that save_kg_conversions updates existing Kg conversions instead of creating duplicates."""
        from npd_management.bom_nutrition import save_kg_conversions
        
        # First save
        payload1 = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1",
            "conversion_factor": 1000.0
        }])
        save_kg_conversions(payload1)
        
        # Verify first save
        doc = frappe.get_doc("Item", "TEST-FIX-ITEM-1")
        kg_convs = [u for u in doc.uoms if u.uom.lower() == "kg"]
        self.assertEqual(len(kg_convs), 1)
        self.assertEqual(flt(kg_convs[0].conversion_factor), 1000.0)
        
        # Second save with different factor
        payload2 = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1",
            "conversion_factor": 2000.0
        }])
        save_kg_conversions(payload2)
        
        # Verify it updated in-place rather than duplicating
        doc.reload()
        kg_convs = [u for u in doc.uoms if u.uom.lower() == "kg"]
        self.assertEqual(len(kg_convs), 1)
        self.assertEqual(flt(kg_convs[0].conversion_factor), 2000.0)

    def test_check_kg_conversions_type_restriction(self):
        """Verify that check_kg_conversions throws error on non-whitelisted doctypes."""
        from npd_management.bom_nutrition import check_kg_conversions
        payload = json.dumps([{
            "item_doctype": "User",
            "item_code": "Administrator"
        }])
        
        with self.assertRaises(frappe.ValidationError):
            check_kg_conversions(payload)

    def test_check_kg_conversions_permissions(self):
        """Verify that check_kg_conversions checks read permissions."""
        from npd_management.bom_nutrition import check_kg_conversions
        payload = json.dumps([{
            "item_doctype": "Item",
            "item_code": "TEST-FIX-ITEM-1"
        }])
        
        frappe.set_user("no-permission-test@example.com")
        try:
            with self.assertRaises(frappe.ValidationError):
                check_kg_conversions(payload)
        finally:
            frappe.set_user("Administrator")

    def test_recalculate_bom_nutrition_permissions(self):
        """Verify that recalculate_bom_nutrition checks write permissions."""
        from npd_management.bom_nutrition import recalculate_bom_nutrition
        
        # Find any existing BOM
        bom_name = frappe.db.get_value("BOM", {}, "name")
        if not bom_name:
            self.skipTest("No BOM records found in database to run recalculate permission test.")
            
        # Switch to unauthorized user
        frappe.set_user("no-permission-test@example.com")
        try:
            with self.assertRaises(frappe.ValidationError):
                recalculate_bom_nutrition(bom_name)
        finally:
            frappe.set_user("Administrator")

    def test_kg_conversion_factor_math(self):
        """Verify that Kg conversion factor math functions correctly using division."""
        from npd_management.utils.nutritional_rollup import get_kg_conversion_factor
        
        # Item with Gram stock UOM and 1000.0 conversion factor for kg
        doc = frappe.get_doc("Item", "TEST-FIX-ITEM-1")
        doc.append("uoms", {
            "uom": "kg",
            "conversion_factor": 1000.0
        })
        doc.save(ignore_permissions=True)
        
        factor = get_kg_conversion_factor("TEST-FIX-ITEM-1", "Item")
        # 1 stock UOM (Gram) = 1.0 / 1000.0 = 0.001 Kg
        self.assertAlmostEqual(factor, 0.001)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNpdManagementFixes)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    import sys
    sys.exit(0 if result.wasSuccessful() else 1)
