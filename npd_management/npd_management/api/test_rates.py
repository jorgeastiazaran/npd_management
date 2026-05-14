import frappe
from npd_management.api.npd_utils import get_erpnext_item_cost

def test_rates():
    item_code = "MP-0286"
    v_rate = get_erpnext_item_cost(item_code, "Valuation Rate")
    p_rate = get_erpnext_item_cost(item_code, "Last Purchase Rate")
    print(f"Item: {item_code}")
    print(f"Valuation Rate: {v_rate}")
    print(f"Last Purchase Rate: {p_rate}")
    
    item_code = "MP-0275"
    v_rate = get_erpnext_item_cost(item_code, "Valuation Rate")
    p_rate = get_erpnext_item_cost(item_code, "Last Purchase Rate")
    print(f"Item: {item_code}")
    print(f"Valuation Rate: {v_rate}")
    print(f"Last Purchase Rate: {p_rate}")
