# -*- coding: utf-8 -*-
"""Shared nutritional rollup for NPD BOM and ERPNext BOM (local DB only)."""
import frappe
from frappe.utils import flt

from npd_management.npd_management.npd_management.doctype.npd_nutritional_profile.npd_nutritional_profile import (
    get_active_profile,
    NUTRITIONAL_FIELDS,
)


def to_grams(qty, uom):
    """Convert a quantity in the given UOM to grams."""
    uom = (uom or "").strip().lower()
    factors = {
        "g": 1.0, "gram": 1.0, "gramo": 1.0, "gramos": 1.0,
        "kg": 1000.0, "kilogram": 1000.0, "kilogramo": 1000.0, "kilogramos": 1000.0,
        "mg": 0.001, "milligram": 0.001, "miligramo": 0.001,
        "lb": 453.592, "pound": 453.592, "libra": 453.592,
        "oz": 28.3495, "ounce": 28.3495, "onza": 28.3495,
    }
    factor = factors.get(uom, 1.0)
    return flt(qty) * factor


def _row_attr(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def rollup_nutrition(items, item_doctype_key="item_doctype", default_item_doctype="NPD Item"):
    """
    Roll up nutrient values from active NPD Nutritional Profiles for BOM rows.

    Args:
        items: child table rows (doc objects or dicts)
        item_doctype_key: field name for row doctype (NPD BOM uses item_doctype)
        default_item_doctype: default when row has no item_doctype (NPD BOM)

    Returns:
        dict mapping each NUTRITIONAL_FIELDS key to per-100g float values.
    """
    totals = {field: 0.0 for field in NUTRITIONAL_FIELDS}
    total_weight_g = 0.0

    for item in items or []:
        if not flt(_row_attr(item, "include_in_nutrient_calc", 1)):
            continue

        item_type = _row_attr(item, item_doctype_key) or default_item_doctype
        item_code = _row_attr(item, "item_code")
        if not item_code:
            continue

        npd_item_code = item_code if item_type == "NPD Item" else None
        erpnext_item_code = item_code if item_type != "NPD Item" else None

        if npd_item_code:
            profile = get_active_profile(npd_item=npd_item_code)
        else:
            profile = get_active_profile(item_code=erpnext_item_code)

        if not profile:
            continue

        if not flt(profile.get("include_in_nutrient_calc", 1)):
            continue

        if npd_item_code and frappe.db.exists("NPD Item", npd_item_code):
            item_flag = frappe.db.get_value("NPD Item", npd_item_code, "npdi_include_in_nutrient_calc")
            if item_flag is not None and not flt(item_flag):
                continue
        elif erpnext_item_code and frappe.db.exists("Item", erpnext_item_code):
            item_flag = frappe.db.get_value("Item", erpnext_item_code, "npdi_include_in_nutrient_calc")
            if item_flag is not None and not flt(item_flag):
                continue

        ref_g = flt(profile.get("reference_quantity_g") or 100.0)
        qty = flt(_row_attr(item, "qty"))
        uom = (_row_attr(item, "uom") or "").lower()
        weight_g = to_grams(qty, uom)
        if weight_g <= 0:
            continue

        total_weight_g += weight_g
        for field in NUTRITIONAL_FIELDS:
            val_per_ref = flt(profile.get(field, 0))
            totals[field] += (val_per_ref / ref_g) * weight_g

    if total_weight_g > 0:
        return {field: totals[field] / total_weight_g * 100.0 for field in NUTRITIONAL_FIELDS}
    return {field: 0.0 for field in NUTRITIONAL_FIELDS}


def apply_rollup_to_doc(doc, totals):
    """Set nutritional field values on a BOM document."""
    for field, value in totals.items():
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
