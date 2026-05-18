# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class NPDBOMComparison(Document):
    pass

@frappe.whitelist()
def get_bom_comparison_json(base_bom, compare_bom):
    """Compares base experimental BOM against standard comparison BOM arrays, evaluating material and operational delta metrics."""
    if not base_bom or not compare_bom:
        return {}
        
    base_doc = frappe.get_doc("BOM", base_bom)
    comp_doc = frappe.get_doc("BOM", compare_bom)
    
    # 1. Map items by item_code into dict arrays
    base_items = {}
    for item in base_doc.get("items"):
        base_items[item.item_code] = {
            "item_name": item.item_name,
            "qty": flt(item.qty),
            "rate": flt(item.rate),
            "amount": flt(item.amount),
            "uom": item.uom
        }
        
    comp_items = {}
    for item in comp_doc.get("items"):
        comp_items[item.item_code] = {
            "item_name": item.item_name,
            "qty": flt(item.qty),
            "rate": flt(item.rate),
            "amount": flt(item.amount),
            "uom": item.uom
        }
        
    # 2. Categorize deltas arraying Added, Removed, and Changed records
    added = []
    removed = []
    changed = []
    unchanged = []
    
    for icode, b_data in base_items.items():
        if icode not in comp_items:
            added.append({
                "item_code": icode,
                "item_name": b_data["item_name"],
                "qty": b_data["qty"],
                "rate": b_data["rate"],
                "amount": b_data["amount"],
                "uom": b_data["uom"],
                "cost_variance": b_data["amount"]
            })
        else:
            c_data = comp_items[icode]
            qty_diff = b_data["qty"] - c_data["qty"]
            rate_diff = b_data["rate"] - c_data["rate"]
            amt_diff = b_data["amount"] - c_data["amount"]
            
            if abs(qty_diff) > 0.0001 or abs(rate_diff) > 0.0001:
                changed.append({
                    "item_code": icode,
                    "item_name": b_data["item_name"],
                    "base_qty": b_data["qty"],
                    "comp_qty": c_data["qty"],
                    "qty_diff": qty_diff,
                    "base_rate": b_data["rate"],
                    "comp_rate": c_data["rate"],
                    "rate_diff": rate_diff,
                    "base_amount": b_data["amount"],
                    "comp_amount": c_data["amount"],
                    "uom": b_data["uom"],
                    "cost_variance": amt_diff
                })
            else:
                unchanged.append({
                    "item_code": icode,
                    "item_name": b_data["item_name"],
                    "qty": b_data["qty"],
                    "rate": b_data["rate"],
                    "amount": b_data["amount"],
                    "uom": b_data["uom"]
                })
                
    for icode, c_data in comp_items.items():
        if icode not in base_items:
            removed.append({
                "item_code": icode,
                "item_name": c_data["item_name"],
                "qty": c_data["qty"],
                "rate": c_data["rate"],
                "amount": c_data["amount"],
                "uom": c_data["uom"],
                "cost_variance": -c_data["amount"]
            })
            
    total_variance = flt(base_doc.total_cost) - flt(comp_doc.total_cost)
    
    return {
        "base_bom": base_bom,
        "compare_bom": compare_bom,
        "base_total_cost": flt(base_doc.total_cost),
        "compare_total_cost": flt(comp_doc.total_cost),
        "total_variance": total_variance,
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged
    }
