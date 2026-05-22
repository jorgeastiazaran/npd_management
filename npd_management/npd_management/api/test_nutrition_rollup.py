# -*- coding: utf-8 -*-
import frappe
from frappe.utils import flt

def run_tests():
    print("=== STARTING NUTRITION ROLLUP AND PROFILE TESTS ===")
    
    # Ensure UOM 'g' exists
    if not frappe.db.exists("UOM", "g"):
        frappe.get_doc({
            "doctype": "UOM",
            "uom_name": "g"
        }).insert(ignore_permissions=True)
        
    # Ensure Item Group 'All Item Groups' exists
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 0
        }).insert(ignore_permissions=True)

    # 1. Clean up any previous test docs to keep it clean
    frappe.db.sql("DELETE FROM `tabNPD Nutritional Profile` WHERE name LIKE 'TEST-NP-%'")
    frappe.db.sql("DELETE FROM `tabNPD BOM Item` WHERE parent LIKE 'TEST-BOM-%'")
    frappe.db.sql("DELETE FROM `tabNPD BOM` WHERE name LIKE 'TEST-BOM-%'")
    frappe.db.sql("DELETE FROM `tabBOM Item` WHERE parent LIKE 'TEST-EBOM-%'")
    frappe.db.sql("DELETE FROM `tabBOM` WHERE name LIKE 'TEST-EBOM-%'")
    
    # Ensure test items exist
    npd_item_1 = "TEST-NPD-ITEM-1"
    npd_item_2 = "TEST-NPD-ITEM-2"
    erp_item_1 = "TEST-ERP-ITEM-1"
    erp_item_2 = "TEST-ERP-ITEM-2"
    
    if not frappe.db.exists("NPD Item", npd_item_1):
        frappe.get_doc({
            "doctype": "NPD Item",
            "item_code": npd_item_1,
            "item_name": "Test NPD Item 1",
            "item_group": "All Item Groups",
            "stock_uom": "g",
            "valuation_rate": 1.5
        }).insert()
        
    if not frappe.db.exists("NPD Item", npd_item_2):
        frappe.get_doc({
            "doctype": "NPD Item",
            "item_code": npd_item_2,
            "item_name": "Test NPD Item 2",
            "item_group": "All Item Groups",
            "stock_uom": "g",
            "valuation_rate": 2.0
        }).insert()

    if not frappe.db.exists("Item", erp_item_1):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": erp_item_1,
            "item_name": "Test ERP Item 1",
            "item_group": "All Item Groups",
            "stock_uom": "g",
            "valuation_rate": 3.0
        }).insert()

    if not frappe.db.exists("Item", erp_item_2):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": erp_item_2,
            "item_name": "Test ERP Item 2",
            "item_group": "All Item Groups",
            "stock_uom": "g",
            "valuation_rate": 4.0
        }).insert()

    print("Step 1: Create Nutritional Profiles and verify default logic")
    # Create Profile A for npd_item_1
    p_a = frappe.get_doc({
        "doctype": "NPD Nutritional Profile",
        "title": "TEST-NP-A",
        "npd_item": npd_item_1,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 200.0,
        "sodio_mg": 50.0
    }).insert()
    
    print(f"Created Profile A: {p_a.name}, is_default={p_a.is_default}")
    
    # Create Profile B for npd_item_1, also set to default
    p_b = frappe.get_doc({
        "doctype": "NPD Nutritional Profile",
        "title": "TEST-NP-B",
        "npd_item": npd_item_1,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 350.0,
        "sodio_mg": 80.0
    }).insert()
    
    print(f"Created Profile B: {p_b.name}, is_default={p_b.is_default}")
    
    # Reload Profile A to verify is_default is now 0
    p_a.reload()
    print(f"After inserting B, Profile A is_default={p_a.is_default} (Expected: 0)")
    assert p_a.is_default == 0, "Profile A should have been unmarked as default"
    
    # Check that NPD Item npdi_default_nutritional_profile was synced
    npd_item_doc = frappe.get_doc("NPD Item", npd_item_1)
    print(f"NPD Item default profile: {npd_item_doc.npdi_default_nutritional_profile} (Expected: {p_b.name})")
    print(f"NPD Item kcal: {npd_item_doc.npdi_nutrition_per_100g_kcal} (Expected: 350.0)")
    assert npd_item_doc.npdi_default_nutritional_profile == p_b.name, "NPD Item default profile not synced"
    assert flt(npd_item_doc.npdi_nutrition_per_100g_kcal) == 350.0, "NPD Item kcal not synced"

    # Create active profile for npd_item_2
    p_c = frappe.get_doc({
        "doctype": "NPD Nutritional Profile",
        "title": "TEST-NP-C",
        "npd_item": npd_item_2,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 100.0,
        "sodio_mg": 10.0
    }).insert()

    print("Step 2: Create NPD BOM and verify costing and nutritional rollup")
    # Let's create an NPD BOM for npd_item_1 using npd_item_1 and npd_item_2
    npd_bom = frappe.get_doc({
        "doctype": "NPD BOM",
        "name": "TEST-BOM-1",
        "item": npd_item_1,
        "item_doctype": "NPD Item",
        "quantity": 1.0,
        "company": "TechFood",
        "conversion_rate": 1.0,
        "items": [
            {
                "item_code": npd_item_1,
                "item_doctype": "NPD Item",
                "qty": 40.0,
                "uom": "g",
                "rate": 1.5,
                "include_in_nutrient_calc": 1
            },
            {
                "item_code": npd_item_2,
                "item_doctype": "NPD Item",
                "qty": 60.0,
                "uom": "g",
                "rate": 2.0,
                "include_in_nutrient_calc": 1
            }
        ]
    })
    npd_bom.insert()
    # Validate calculates rates and nutrition
    npd_bom.validate()
    
    # Expected kcal = (350/100)*40 + (100/100)*60 = 140 + 60 = 200 kcal for 100g (since total weight is 100g)
    # Expected sodio = (80/100)*40 + (10/100)*60 = 32 + 6 = 38 mg per 100g
    print(f"NPD BOM calculated kcal: {npd_bom.contenido_energetico_kcal} (Expected: 200.0)")
    print(f"NPD BOM calculated sodio: {npd_bom.sodio_mg} (Expected: 38.0)")
    assert flt(npd_bom.contenido_energetico_kcal) == 200.0, "NPD BOM kcal rollup incorrect"
    assert flt(npd_bom.sodio_mg) == 38.0, "NPD BOM sodio rollup incorrect"
    
    # Check costing:
    # item 1 rate = 1.5, qty = 40 => amount = 60
    # item 2 rate = 2.0, qty = 60 => amount = 120
    # Total cost = 180
    print(f"NPD BOM total cost: {npd_bom.total_cost} (Expected: 180.0)")
    assert flt(npd_bom.total_cost) == 180.0, "NPD BOM costing calculation incorrect"

    print("Step 3: Submit NPD BOM and check profile lock")
    npd_bom.submit()
    
    p_b.reload()
    p_c.reload()
    print(f"Profile B is_locked: {p_b.is_locked} (Expected: 1)")
    print(f"Profile C is_locked: {p_c.is_locked} (Expected: 1)")
    assert p_b.is_locked == 1, "Profile B should be locked"
    assert p_c.is_locked == 1, "Profile C should be locked"
    
    # Try updating Profile B, should fail validation
    p_b.contenido_energetico_kcal = 400.0
    try:
        p_b.save()
        raise Exception("Updating locked profile should have failed validation!")
    except frappe.ValidationError as e:
        print("Success: ValidationError caught as expected when trying to update locked profile")
    except Exception as e:
        if "bloqueado" in str(e) or "locked" in str(e):
            print("Success: Error caught as expected when trying to update locked profile:", str(e))
        else:
            raise

    # 4. Standard ERPNext BOM test
    print("Step 4: Create active nutritional profiles for standard ERPNext Items")
    p_erp_1 = frappe.get_doc({
        "doctype": "NPD Nutritional Profile",
        "title": "TEST-NP-ERP-1",
        "item_code": erp_item_1,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 150.0,
        "sodio_mg": 30.0
    }).insert()
    
    p_erp_2 = frappe.get_doc({
        "doctype": "NPD Nutritional Profile",
        "title": "TEST-NP-ERP-2",
        "item_code": erp_item_2,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 250.0,
        "sodio_mg": 70.0
    }).insert()

    # Verify standard Item custom fields synced
    erp_item_1_doc = frappe.get_doc("Item", erp_item_1)
    print(f"Item 1 default profile: {erp_item_1_doc.npdi_default_nutritional_profile} (Expected: {p_erp_1.name})")
    print(f"Item 1 kcal: {erp_item_1_doc.npdi_nutrition_per_100g_kcal} (Expected: 150.0)")
    assert erp_item_1_doc.npdi_default_nutritional_profile == p_erp_1.name, "Item 1 profile sync failed"
    assert flt(erp_item_1_doc.npdi_nutrition_per_100g_kcal) == 150.0, "Item 1 kcal sync failed"

    print("Step 5: Create Standard BOM and verify rollup")
    # Create standard BOM
    ebom = frappe.get_doc({
        "doctype": "BOM",
        "name": "TEST-EBOM-1",
        "item": erp_item_1,
        "quantity": 1.0,
        "company": "TechFood",
        "conversion_rate": 1.0,
        "is_active": 1,
        "uom": "g",
        "items": [
            {
                "item_code": erp_item_1,
                "qty": 50.0,
                "uom": "g",
                "rate": 3.0,
                "include_in_nutrient_calc": 1
            },
            {
                "item_code": erp_item_2,
                "qty": 50.0,
                "uom": "g",
                "rate": 4.0,
                "include_in_nutrient_calc": 1
            }
        ]
    })
    ebom.insert()
    # The validate hook should calculate nutrition automatically
    ebom.validate()
    
    # Expected kcal: (150/100)*50 + (250/100)*50 = 75 + 125 = 200 kcal / 100g
    # Expected sodio: (30/100)*50 + (70/100)*50 = 15 + 35 = 50 mg / 100g
    print(f"Standard BOM calculated kcal: {ebom.contenido_energetico_kcal} (Expected: 200.0)")
    print(f"Standard BOM calculated sodio: {ebom.sodio_mg} (Expected: 50.0)")
    assert flt(ebom.contenido_energetico_kcal) == 200.0, "Standard BOM kcal rollup incorrect"
    assert flt(ebom.sodio_mg) == 50.0, "Standard BOM sodio rollup incorrect"

    print("Step 6: Submit standard BOM and check locking")
    ebom.submit()
    p_erp_1.reload()
    p_erp_2.reload()
    print(f"ERP Profile 1 locked: {p_erp_1.is_locked} (Expected: 1)")
    print(f"ERP Profile 2 locked: {p_erp_2.is_locked} (Expected: 1)")
    assert p_erp_1.is_locked == 1, "ERP Profile 1 should be locked"
    assert p_erp_2.is_locked == 1, "ERP Profile 2 should be locked"
    
    # Clean up
    frappe.db.rollback()
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
