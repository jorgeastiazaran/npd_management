# -*- coding: utf-8 -*-
"""Nutritional rollup for standard ERPNext BOM (local DB only)."""
import frappe
from frappe.utils import flt

from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import (
    lock_profile,
)
from npd_management.utils.nutritional_rollup import (
    apply_rollup_to_doc,
    collect_profile_names_from_items,
    rollup_nutrition,
)


def _is_locked(doc):
    return flt(getattr(doc, "nutritional_snapshot_locked", 0))


def calculate_nutrition(doc):
    """Roll up nutrients onto BOM from Item-linked nutritional profiles."""
    if _is_locked(doc):
        return

    totals = rollup_nutrition(
        doc.items,
        item_doctype_key="item_doctype",
        default_item_doctype="Item",
    )
    totals.pop("warnings", [])
    apply_rollup_to_doc(doc, totals)


def calculate(doc, method=None):
    calculate_nutrition(doc)


def on_submit(doc, method=None):
    """Lock profiles and freeze nutritional snapshot on BOM submit."""
    for profile_name in collect_profile_names_from_items(
        doc.items,
        item_doctype_key="item_doctype",
        default_item_doctype="Item",
    ):
        lock_profile(profile_name)

    frappe.db.set_value("BOM", doc.name, "nutritional_snapshot_locked", 1, update_modified=False)


@frappe.whitelist()
def check_kg_conversions(items_json):
    """Scan BOM items JSON for missing Kg conversions."""
    import json
    items = json.loads(items_json)
    
    # Validate doctype and read permissions
    for row in items:
        doctype = row.get("item_doctype", "Item")
        if doctype not in ["Item", "NPD Item"]:
            frappe.throw("Invalid DocType specified for Kg conversions.")
        doc = frappe.get_doc(doctype, row.get("item_code"))
        frappe.has_permission(doctype, "read", doc=doc, throw=True)
        
    from npd_management.utils.nutritional_rollup import check_missing_kg_conversions
    return check_missing_kg_conversions(items, item_doctype_key="item_doctype", default_item_doctype="Item")


@frappe.whitelist()
def save_kg_conversions(conversions):
    """Save explicit Kg conversion factors directly into the Item's UOM table."""
    import json
    conversions_list = json.loads(conversions)
    
    for row in conversions_list:
        doctype = row.get("item_doctype", "Item")
        item_code = row.get("item_code")
        factor = flt(row.get("conversion_factor"))
        
        if doctype not in ["Item", "NPD Item"]:
            frappe.throw("Invalid DocType specified for Kg conversions.")
            
        if factor <= 0:
            frappe.throw("Conversion factor must be greater than zero.")
            
        # Verify user has write permissions on the document
        doc = frappe.get_doc(doctype, item_code)
        frappe.has_permission(doctype, "write", doc=doc, throw=True)
        
        # Check if a UOM entry for "Kg" already exists to avoid duplicates (upsert pattern)
        existing_uom = None
        for u in doc.get("uoms", []):
            if (u.uom or "").lower() == "kg":
                existing_uom = u
                break
                
        if existing_uom:
            existing_uom.conversion_factor = factor
        else:
            doc.append("uoms", {
                "uom": "Kg",
                "conversion_factor": factor
            })
            
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.save()
        
    return True


@frappe.whitelist()
def recalculate_bom_nutrition(bom_name):
    """Manual recalculation from BOM form (client script)."""
    # Verify write permissions on the BOM document
    doc = frappe.get_doc("BOM", bom_name)
    frappe.has_permission("BOM", "write", doc=doc, throw=True)
    
    if _is_locked(doc):
        frappe.throw("Nutritional values are locked because this BOM was submitted.")
    calculate_nutrition(doc)
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def calculate_nutrition_for_doc(doc_json):
    """Dynamic calculation of nutrition for an unsaved BOM document."""
    import json
    from npd_management.utils.nutritional_rollup import rollup_nutrition
    doc_dict = json.loads(doc_json)
    
    totals = rollup_nutrition(
        doc_dict.get("items", []),
        item_doctype_key="item_doctype",
        default_item_doctype="Item",
        parent_ref_qty=doc_dict.get("npdi_reference_quantity_g", 100.0)
    )
    warnings = totals.pop("warnings", [])
    
    return {
        "totals": totals,
        "warnings": warnings
    }


@frappe.whitelist()
def create_nutritional_profile_from_bom(bom_name):
    """Create a new Nutritional Profile from a standard BOM's calculated nutrition."""
    bom = frappe.get_doc("BOM", bom_name)
    if not bom.item:
        frappe.throw("Please specify an Item for this BOM first.")

    from npd_management.npd_management.doctype.nutritional_profile.nutritional_profile import (
        NUTRITIONAL_FIELDS,
    )

    doc = frappe.new_doc("Nutritional Profile")
    doc.reference_doctype = "Item"
    doc.reference_name = bom.item
    doc.item_name = bom.item_name or frappe.db.get_value("Item", bom.item, "item_name") or bom.item
    doc.is_default = 0
    doc.reference_quantity_g = flt(bom.get("npdi_reference_quantity_g") or 100.0)
    doc.include_in_nutrient_calc = 1

    for field in NUTRITIONAL_FIELDS:
        if hasattr(bom, field):
            setattr(doc, field, flt(getattr(bom, field, 0)))

    doc.insert()
    return doc.name
