import frappe
from frappe.utils import flt
from npd_management.utils.nutritional_rollup import (
    check_missing_kg_conversions,
    rollup_nutrition,
    get_kg_conversion_factor
)
from npd_management.bom_nutrition import save_kg_conversions
import json

def run_tests():
    print("--- Starting Kg Conversion Tests ---")

    for u in ["Kg", "Gram", "Litre", "Nos"]:
        if not frappe.db.exists("UOM", u):
            frappe.get_doc({
                "doctype": "UOM",
                "uom_name": u,
                "must_be_whole_number": 0
            }).insert(ignore_permissions=True)

    # 1. Setup mock items
    items_created = []
    
    def get_or_create(code, name, suom, wpu=0, wuom=None):
        if not frappe.db.exists("NPD Item", {"item_name": name}):
            doc = frappe.get_doc({
                "doctype": "NPD Item",
                "item_name": name,
                "stock_uom": suom,
                "weight_per_unit": wpu,
                "weight_uom": wuom,
                "item_group": "All Item Groups",
                "npdi_include_in_nutrient_calc": 1
            }).insert(ignore_permissions=True, ignore_mandatory=True)
            return doc.name
        else:
            return frappe.db.get_value("NPD Item", {"item_name": name}, "name")

    id1 = get_or_create("TEST-KG-1", "Test Item 1 (Gram)", "Gram")
    id2 = get_or_create("TEST-KG-2", "Test Item 2 (Litre)", "Litre", 1.05, "Kg")
    id3 = get_or_create("TEST-KG-3", "Test Item 3 (Nos)", "Nos")

    # Create dummy nutritional profiles
    def create_profile(item_code):
        if not frappe.db.exists("Nutritional Profile", {"reference_doctype": "NPD Item", "reference_name": item_code}):
            frappe.get_doc({
                "doctype": "Nutritional Profile",
                "reference_doctype": "NPD Item",
                "reference_name": item_code,
                "is_default": 1,
                "docstatus": 1,
                "reference_quantity_g": 100.0,
                "contenido_energetico_kcal": 100
            }).insert(ignore_permissions=True, ignore_mandatory=True)
            
    create_profile(id1)
    create_profile(id2)
    create_profile(id3)

    # 2. Test missing conversions API
    items = [
        {"item_code": id1, "item_doctype": "NPD Item", "include_in_nutrient_calc": 1, "stock_uom": "Gram", "stock_qty": 500},
        {"item_code": id2, "item_doctype": "NPD Item", "include_in_nutrient_calc": 1, "stock_uom": "Litre", "stock_qty": 2},
        {"item_code": id3, "item_doctype": "NPD Item", "include_in_nutrient_calc": 1, "stock_uom": "Nos", "stock_qty": 10},
    ]
    
    missing = check_missing_kg_conversions(items)
    print(f"Missing conversions: {len(missing)}")
    for m in missing:
        print(f"  {m['item_code']} ({m['stock_uom']}): suggested {m['suggested_conversion']}")
        
    # The expected suggestions are:
    # id1 (Gram): 1000.0 (1 Kg = 1000 Gram)
    # id2 (Litre): ~0.95238 (1 Kg = 1 / 1.05 L)
    # id3 (Nos): "" (No weight set)
    
    # 3. Save conversions using the API
    conversions = [
        {"item_code": id1, "item_doctype": "NPD Item", "conversion_factor": 1000.0},
        {"item_code": id2, "item_doctype": "NPD Item", "conversion_factor": 0.95238095},
        {"item_code": id3, "item_doctype": "NPD Item", "conversion_factor": 2.5}, # 1 Kg = 2.5 Nos
    ]
    
    save_kg_conversions(json.dumps(conversions))
    
    # 4. Check missing again
    missing_after = check_missing_kg_conversions(items)
    print(f"Missing conversions after save: {len(missing_after)}")
    
    # 5. Test rollup Kg yield calculation
    f1 = get_kg_conversion_factor(id1, "NPD Item") # 1/1000 = 0.001
    f2 = get_kg_conversion_factor(id2, "NPD Item") # 1/0.95238095 = 1.05
    f3 = get_kg_conversion_factor(id3, "NPD Item") # 1/2.5 = 0.4
    
    print(f"Kg Factors: id1={f1}, id2={f2}, id3={f3}")
    
    # Expected total yield:
    # 500 g * 0.001 = 0.5 Kg
    # 2 L * 1.05 = 2.1 Kg
    # 10 Pieces * 0.4 = 4.0 Kg
    # Total = 6.6 Kg
    
    rollup = rollup_nutrition(items)
    print(f"Calculated Total Yield: {rollup.get('total_yield_kg')} Kg")
    
    if abs(rollup.get("total_yield_kg", 0) - 6.6) < 0.01:
        print("SUCCESS! Kg Yield matched.")
    else:
        print("FAIL! Kg Yield did not match.")
        
    print("--- Tests Finished ---")

if __name__ == "__main__":
    run_tests()
