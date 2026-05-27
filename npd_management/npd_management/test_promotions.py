# -*- coding: utf-8 -*-
import frappe
from frappe.utils import flt

def run_tests():
    print("=== STARTING NPD TO ERP PROMOTION TESTS ===")
    
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
        
    # Ensure Supplier Group 'Raw Material' exists
    if not frappe.db.exists("Supplier Group", "Raw Material"):
        frappe.get_doc({
            "doctype": "Supplier Group",
            "supplier_group_name": "Raw Material",
            "is_group": 0
        }).insert(ignore_permissions=True)

    # 1. Cleanup previous test records
    frappe.db.sql("DELETE FROM `tabNutritional Profile` WHERE reference_name LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabItem` WHERE item_code LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabNPD Item` WHERE name LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabSupplier` WHERE supplier_name LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabNPD Supplier` WHERE name LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabQuotation` WHERE custom_npd_quotation_reference LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabNPD Quotation` WHERE name LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabSupplier Quotation` WHERE custom_npd_sq_reference LIKE 'TEST-PROMOTE-%'")
    frappe.db.sql("DELETE FROM `tabNPD Supplier Quotation` WHERE name LIKE 'TEST-PROMOTE-%'")
    frappe.db.commit()

    print("Step 1: Test NPD Item to standard Item promotion")
    # Create source NPD Item
    npd_item_name = "TEST-PROMOTE-NPD-1"
    npd_item = frappe.get_doc({
        "doctype": "NPD Item",
        "name": npd_item_name,
        "item_code": npd_item_name,
        "item_name": "Test Promote NPD Item 1",
        "item_group": "All Item Groups",
        "stock_uom": "g",
        "valuation_rate": 1.5,
        "naming_series": "NPD-MP-",
        "npdi_include_in_nutrient_calc": 1
    }).db_insert()
    
    # Add Nutritional Profile for it
    p_npd = frappe.get_doc({
        "doctype": "Nutritional Profile",
        "title": "TEST-NP-PROMOTE",
        "reference_doctype": "NPD Item",
        "reference_name": npd_item_name,
        "is_default": 1,
        "reference_quantity_g": 100,
        "contenido_energetico_kcal": 300.0,
        "sodio_mg": 50.0
    }).insert()
    
    # Sync back defaults
    npd_item_doc = frappe.get_doc("NPD Item", npd_item_name)
    npd_item_doc.npdi_default_nutritional_profile = p_npd.name
    npd_item_doc.npdi_nutrition_per_100g_kcal = 300.0
    npd_item_doc.save(ignore_permissions=True)
    
    # Create standard Item linking to it
    erp_item_code = "TEST-PROMOTE-ERP-ITEM-1"
    erp_item = frappe.get_doc({
        "doctype": "Item",
        "item_code": erp_item_code,
        "item_name": "Test Promote ERP Item 1",
        "item_group": "All Item Groups",
        "stock_uom": "g",
        "valuation_rate": 1.5,
        "custom_npd_reference": npd_item_name
    }).insert(ignore_permissions=True)
    
    # Verify hook output
    npd_item_doc.reload()
    print(f"NPD Item is_promoted: {npd_item_doc.is_promoted} (Expected: 1)")
    print(f"NPD Item linked_item: {npd_item_doc.linked_item} (Expected: {erp_item_code})")
    assert npd_item_doc.is_promoted == 1, "NPD Item should be marked as promoted"
    assert npd_item_doc.linked_item == erp_item_code, "NPD Item linked_item mismatch"
    
    # Verify copied Nutritional Profile
    copied_profiles = frappe.get_all("Nutritional Profile", filters={
        "reference_doctype": "Item",
        "reference_name": erp_item_code
    })
    print(f"Copied profiles count: {len(copied_profiles)} (Expected: 1)")
    assert len(copied_profiles) == 1, "Nutritional profile was not copied to the promoted Item"
    
    p_copied = frappe.get_doc("Nutritional Profile", copied_profiles[0].name)
    print(f"Copied profile kcal: {p_copied.contenido_energetico_kcal} (Expected: 300.0)")
    print(f"Copied profile sodio: {p_copied.sodio_mg} (Expected: 50.0)")
    assert flt(p_copied.contenido_energetico_kcal) == 300.0, "Copied profile kcal mismatch"
    assert flt(p_copied.sodio_mg) == 50.0, "Copied profile sodio mismatch"
    
    # Verify standard Item default profile sync
    erp_item.reload()
    print(f"ERP Item active profile: {erp_item.npdi_default_nutritional_profile} (Expected: {p_copied.name})")
    print(f"ERP Item kcal: {erp_item.npdi_nutrition_per_100g_kcal} (Expected: 300.0)")
    assert erp_item.npdi_default_nutritional_profile == p_copied.name, "ERP Item default profile not synced"
    assert flt(erp_item.npdi_nutrition_per_100g_kcal) == 300.0, "ERP Item kcal not synced"

    print("Step 2: Test NPD Supplier to Supplier promotion")
    # Create source NPD Supplier
    npd_supplier_name = "TEST-PROMOTE-NPD-SUP-1"
    npd_supplier = frappe.get_doc({
        "doctype": "NPD Supplier",
        "name": npd_supplier_name,
        "supplier_name": "TEST-PROMOTE-NPD-SUP-1",
        "supplier_group": "Raw Material",
        "evaluation_status": "Approved"
    }).insert(ignore_permissions=True)
    
    # Create standard Supplier linking to it
    erp_supplier_name = "TEST-PROMOTE-ERP-SUP-1"
    erp_supplier = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": erp_supplier_name,
        "supplier_group": "Raw Material",
        "custom_npd_supplier_reference": npd_supplier_name
    }).insert(ignore_permissions=True)
    
    # Verify hook output
    npd_supplier.reload()
    print(f"NPD Supplier is_promoted: {npd_supplier.is_promoted} (Expected: 1)")
    print(f"NPD Supplier linked_supplier: {npd_supplier.linked_supplier} (Expected: {erp_supplier.name})")
    assert npd_supplier.is_promoted == 1, "NPD Supplier should be marked as promoted"
    assert npd_supplier.linked_supplier == erp_supplier.name, "NPD Supplier linked_supplier mismatch"

    print("Step 3: Test NPD Quotation to Quotation promotion")
    # Ensure test customer exists
    if not frappe.db.exists("Customer", "TEST-PROMOTE-CUSTOMER-1"):
        if not frappe.db.exists("Customer Group", "All Customer Groups"):
            frappe.get_doc({
                "doctype": "Customer Group",
                "customer_group_name": "All Customer Groups",
                "is_group": 1
            }).insert(ignore_permissions=True)
        if not frappe.db.exists("Territory", "All Territories"):
            frappe.get_doc({
                "doctype": "Territory",
                "territory_name": "All Territories",
                "is_group": 1
            }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "TEST-PROMOTE-CUSTOMER-1",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        }).insert(ignore_permissions=True)

    # Create source NPD Quotation
    npd_qtn = frappe.get_doc({
        "doctype": "NPD Quotation",
        "name": "TEST-PROMOTE-NPD-QTN-1",
        "status": "Approved",
        "quotation_to": "Customer",
        "party_name": "TEST-PROMOTE-CUSTOMER-1",
        "transaction_date": "2026-05-26",
        "valid_till": "2026-06-26",
        "company": "TechFood",
        "currency": "MXN",
        "items": [
            {
                "npd_item": npd_item_name,
                "qty": 100,
                "rate": 2.5
            }
        ]
    }).insert(ignore_permissions=True)
    
    # Create standard Quotation linking to it
    if not frappe.db.exists("Price List", "Standard Selling"):
        frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": "Standard Selling",
            "enabled": 1,
            "buying": 0,
            "selling": 1,
            "currency": "MXN"
        }).insert(ignore_permissions=True)

    erp_qtn = frappe.get_doc({
        "doctype": "Quotation",
        "quotation_to": "Customer",
        "party_name": "TEST-PROMOTE-CUSTOMER-1",
        "transaction_date": "2026-05-26",
        "valid_till": "2026-06-26",
        "company": "TechFood",
        "currency": "MXN",
        "selling_price_list": "Standard Selling",
        "price_list_currency": "MXN",
        "plc_conversion_rate": 1.0,
        "conversion_rate": 1.0,
        "custom_npd_quotation_reference": npd_qtn.name,
        "items": [
            {
                "item_code": erp_item_code,
                "qty": 100,
                "rate": 2.5
            }
        ]
    }).insert(ignore_permissions=True)
    
    # Verify hook output
    npd_qtn.reload()
    print(f"NPD Quotation is_promoted: {npd_qtn.is_promoted} (Expected: 1)")
    print(f"NPD Quotation promoted_quotation: {npd_qtn.promoted_quotation} (Expected: {erp_qtn.name})")
    print(f"NPD Quotation status: {npd_qtn.status} (Expected: Promoted)")
    assert npd_qtn.is_promoted == 1, "NPD Quotation should be marked as promoted"
    assert npd_qtn.promoted_quotation == erp_qtn.name, "NPD Quotation promoted_quotation mismatch"
    assert npd_qtn.status == "Promoted", "NPD Quotation status should be Promoted"

    print("Step 4: Test NPD Supplier Quotation to Supplier Quotation promotion")
    # Create source NPD Supplier Quotation
    npd_sq = frappe.get_doc({
        "doctype": "NPD Supplier Quotation",
        "name": "TEST-PROMOTE-NPD-SQ-1",
        "supplier": npd_supplier_name,
        "transaction_date": "2026-05-26",
        "company": "TechFood",
        "currency": "MXN",
        "status": "Draft",
        "items": [
            {
                "item_code": npd_item_name,
                "qty": 100,
                "uom": "g",
                "rate": 1.2
            }
        ]
    }).insert(ignore_permissions=True)
    
    # Create standard Supplier Quotation linking to it
    if not frappe.db.exists("Price List", "Standard Buying"):
        frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": "Standard Buying",
            "enabled": 1,
            "buying": 1,
            "selling": 0,
            "currency": "MXN"
        }).insert(ignore_permissions=True)

    erp_sq = frappe.get_doc({
        "doctype": "Supplier Quotation",
        "supplier": erp_supplier.name,
        "transaction_date": "2026-05-26",
        "company": "TechFood",
        "currency": "MXN",
        "buying_price_list": "Standard Buying",
        "price_list_currency": "MXN",
        "plc_conversion_rate": 1.0,
        "conversion_rate": 1.0,
        "custom_npd_sq_reference": npd_sq.name,
        "items": [
            {
                "item_code": erp_item_code,
                "qty": 100,
                "uom": "g",
                "warehouse": "Finished Goods - TF",
                "rate": 1.2
            }
        ]
    }).insert(ignore_permissions=True)
    
    # Verify hook output
    npd_sq.reload()
    print(f"NPD SQ is_promoted: {npd_sq.is_promoted} (Expected: 1)")
    print(f"NPD SQ linked_sq: {npd_sq.linked_sq} (Expected: {erp_sq.name})")
    assert npd_sq.is_promoted == 1, "NPD Supplier Quotation should be marked as promoted"
    assert npd_sq.linked_sq == erp_sq.name, "NPD Supplier Quotation linked_sq mismatch"

    # Roll back transaction to keep the test environment clean
    frappe.db.rollback()
    print("=== ALL NPD TO ERP PROMOTION TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
