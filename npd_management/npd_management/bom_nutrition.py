# -*- coding: utf-8 -*-
"""Nutritional rollup for standard ERPNext BOM (local DB only)."""
import frappe
from frappe.utils import flt

from npd_management.npd_management.doctype.npd_nutritional_profile.npd_nutritional_profile import (
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
def recalculate_bom_nutrition(bom_name):
    """Manual recalculation from BOM form (client script)."""
    doc = frappe.get_doc("BOM", bom_name)
    if _is_locked(doc):
        frappe.throw("Nutritional values are locked because this BOM was submitted.")
    calculate_nutrition(doc)
    doc.save()
    return doc.as_dict()
