# -*- coding: utf-8 -*-
"""Shared nutritional rollup for NPD BOM and ERPNext BOM (local DB only)."""
import frappe
from frappe.utils import flt

from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import (
    get_active_profile,
    NUTRITIONAL_FIELDS,
)


def get_static_kg_factor(uom):
    """Return the Kg equivalent of 1 unit of a known mass UOM."""
    uom = (uom or "").strip().lower()
    factors = {
        "kg": 1.0, "kilogram": 1.0, "kilogramo": 1.0, "kilogramos": 1.0,
        "g": 0.001, "gram": 0.001, "gramo": 0.001, "gramos": 0.001,
        "mg": 0.000001, "milligram": 0.000001, "miligramo": 0.000001,
        "lb": 0.453592, "pound": 0.453592, "libra": 0.453592,
        "oz": 0.0283495, "ounce": 0.0283495, "onza": 0.0283495,
    }
    return factors.get(uom)


def get_kg_conversion_factor(item_code, item_doctype):
    """
    Return the multiplier to convert stock_qty to Kg.
    
    ERPNext stores the conversion factor in the uoms child table as:
    1 unit of UOM (e.g. Kg) = conversion_factor * (1 unit of stock_uom, e.g. Gram).
    So for Stock UOM Gram and conversion UOM Kg, conversion_factor = 1000.0.
    
    To convert stock_qty (in stock_uom) to Kg weight, we divide:
    weight_kg = stock_qty / conversion_factor.
    This corresponds to multiplying stock_qty by (1.0 / conversion_factor).
    """
    try:
        doc = frappe.get_cached_doc(item_doctype, item_code)
    except frappe.DoesNotExistError:
        return 0.0
    stock_uom = doc.get("stock_uom") or ""
    if stock_uom.lower() == "kg":
        return 1.0
    for u in doc.get("uoms", []):
        uom_name = getattr(u, "uom", None) or (u.get("uom") if isinstance(u, dict) else "")
        conv_factor = flt(getattr(u, "conversion_factor", None) or (u.get("conversion_factor") if isinstance(u, dict) else 0))
        if (uom_name or "").lower() == "kg":
            return 1.0 / conv_factor if conv_factor else 0.0
            
    # Fallback to static UOM translation if no database conversion is configured
    static_factor = get_static_kg_factor(stock_uom)
    if static_factor is not None:
        return static_factor
    return 0.0


def check_missing_kg_conversions(items, item_doctype_key="item_doctype", default_item_doctype="NPD Item"):
    """
    Scan BOM items for ingredients that lack an explicit Kg conversion.
    Returns a list of dicts with suggestions for missing conversions.
    """
    missing = []
    seen = set()

    for item in items or []:
        if not flt(_row_attr(item, "include_in_nutrient_calc", 1)):
            continue

        item_code = _row_attr(item, "item_code")
        if not item_code or item_code in seen:
            continue

        item_type = _row_attr(item, item_doctype_key) or default_item_doctype
        try:
            doc = frappe.get_cached_doc(item_type, item_code)
        except frappe.DoesNotExistError:
            seen.add(item_code)
            continue

        if (doc.stock_uom or "").lower() == "kg":
            seen.add(item_code)
            continue

        has_kg = False
        for u in doc.get("uoms", []):
            if (u.uom or "").lower() == "kg":
                has_kg = True
                break

        if not has_kg:
            suggested = ""
            static_factor = get_static_kg_factor(doc.get("stock_uom"))
            if static_factor:
                # 1 stock_uom = static_factor Kg -> 1 Kg = (1/static_factor) stock_uom
                suggested = 1.0 / static_factor
            else:
                weight_per_unit = doc.get("weight_per_unit")
                weight_uom = doc.get("weight_uom")
                if weight_per_unit and weight_uom:
                    w_factor = get_static_kg_factor(weight_uom)
                    if w_factor:
                        suggested = 1.0 / (flt(weight_per_unit) * w_factor)

            missing.append({
                "item_code": item_code,
                "item_doctype": item_type,
                "stock_uom": doc.stock_uom,
                "suggested_conversion": suggested
            })
        
        seen.add(item_code)

    return missing


def _row_attr(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def rollup_nutrition(items, item_doctype_key="item_doctype", default_item_doctype="NPD Item", parent_ref_qty=100.0):
    """
    Roll up nutrient values from active NPD Nutritional Profiles for BOM rows.

    Args:
        items: child table rows (doc objects or dicts)
        item_doctype_key: field name for row doctype (NPD BOM uses item_doctype)
        default_item_doctype: default when row has no item_doctype (NPD BOM)
        parent_ref_qty: The reference quantity (g) of the parent BOM

    Returns:
        dict mapping each NUTRITIONAL_FIELDS key to per-100g float values.
    """
    totals = {field: 0.0 for field in NUTRITIONAL_FIELDS}
    total_weight_kg = 0.0
    warnings = []
    
    # Memoization caches
    profile_cache = {}
    kg_multiplier_cache = {}

    for item in items or []:
        if not flt(_row_attr(item, "include_in_nutrient_calc", 1)):
            continue

        item_type = _row_attr(item, item_doctype_key) or default_item_doctype
        item_code = _row_attr(item, "item_code")
        if not item_code:
            continue

        npd_item_code = item_code if item_type == "NPD Item" else None
        erpnext_item_code = item_code if item_type != "NPD Item" else None

        cache_key = (npd_item_code, erpnext_item_code)
        if cache_key in profile_cache:
            profile = profile_cache[cache_key]
        else:
            if npd_item_code:
                profile = get_active_profile(npd_item=npd_item_code)
            else:
                profile = get_active_profile(item_code=erpnext_item_code)
            profile_cache[cache_key] = profile

        if not profile:
            continue

        if not flt(profile.get("include_in_nutrient_calc", 1)):
            continue

        if npd_item_code and frappe.db.exists("NPD Item", npd_item_code):
            try:
                item_flag = frappe.db.get_value("NPD Item", npd_item_code, "npdi_include_in_nutrient_calc")
                if item_flag is not None and not flt(item_flag):
                    continue
            except Exception:
                pass
        elif erpnext_item_code and frappe.db.exists("Item", erpnext_item_code):
            try:
                item_flag = frappe.db.get_value("Item", erpnext_item_code, "npdi_include_in_nutrient_calc")
                if item_flag is not None and not flt(item_flag):
                    continue
            except Exception:
                pass

        ref_g = flt(profile.get("reference_quantity_g") or 100.0)
        
        if ref_g != flt(parent_ref_qty):
            warnings.append(
                f"Discrepancy: Item '{item_code}' has reference quantity {ref_g}g, which differs from the BOM's reference quantity {flt(parent_ref_qty)}g."
            )
            
        ref_kg = ref_g / 1000.0
        if ref_kg <= 0:
            ref_kg = 0.1

        # Use stock_qty and explicit Kg conversion multiplier
        stock_qty = flt(_row_attr(item, "stock_qty"))
        if stock_qty <= 0:
            # Fallback if stock_qty isn't computed in a custom scenario
            qty = flt(_row_attr(item, "qty"))
            conv = flt(_row_attr(item, "conversion_factor") or 1.0)
            stock_qty = qty * conv

        conv_cache_key = (item_code, item_type)
        if conv_cache_key not in kg_multiplier_cache:
            kg_multiplier_cache[conv_cache_key] = get_kg_conversion_factor(item_code, item_type)
            
        kg_multiplier = kg_multiplier_cache[conv_cache_key]
        weight_kg = stock_qty * kg_multiplier
        
        if weight_kg <= 0:
            continue

        total_weight_kg += weight_kg
        for field in NUTRITIONAL_FIELDS:
            val_per_ref = flt(profile.get(field, 0))
            totals[field] += (val_per_ref / ref_kg) * weight_kg

    result = {}
    if total_weight_kg > 0:
        result = {field: totals[field] / total_weight_kg * (flt(parent_ref_qty) / 1000.0) for field in NUTRITIONAL_FIELDS}
    else:
        result = {field: 0.0 for field in NUTRITIONAL_FIELDS}
        
    result["total_yield_kg"] = total_weight_kg
    result["warnings"] = warnings
    return result


def apply_rollup_to_doc(doc, totals):
    """Set nutritional field values on a BOM document."""
    for field, value in totals.items():
        if field == "total_yield_kg":
            if hasattr(doc, "npdi_total_yield_kg"):
                doc.npdi_total_yield_kg = value
        elif hasattr(doc, field):
            setattr(doc, field, value)


def collect_profile_names_from_items(items, item_doctype_key="item_doctype", default_item_doctype="NPD Item"):
    """Return unique active profile names referenced by BOM rows."""
    names = []
    seen = set()
    for item in items or []:
        item_type = _row_attr(item, item_doctype_key) or default_item_doctype
        item_code = _row_attr(item, "item_code")
        if not item_code:
            continue
        npd_item_code = item_code if item_type == "NPD Item" else None
        erpnext_item_code = item_code if item_type != "NPD Item" else None
        profile = get_active_profile(npd_item=npd_item_code, item_code=erpnext_item_code)
        if profile and profile.get("name") and profile["name"] not in seen:
            seen.add(profile["name"])
            names.append(profile["name"])
    return names
