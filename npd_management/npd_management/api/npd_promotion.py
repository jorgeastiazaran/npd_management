# -*- coding: utf-8 -*-
"""
npd_promotion.py — Shared promotion engine for all NPD → Production doctype flows.

Usage in a doctype class:
    from npd_management.api.npd_promotion import NpdPromotionMixin, build_promotion_data

    class NPDFoo(NpdPromotionMixin, Document):
        TARGET_DOCTYPE = "Foo"
        NPD_ONLY_FIELDS = {"is_promoted", "linked_foo", ...}
        CHILD_TABLE_FIELDS = ["items", ...]

        @frappe.whitelist()
        @staticmethod
        def get_promotion_data(doc_name):
            return NpdPromotionMixin.default_get_promotion_data(
                "NPD Foo", doc_name
            )
"""
import frappe

# Row-level keys Frappe adds that must be stripped before passing to a new doc
_ROW_META_KEYS = frozenset({
    "name", "parent", "parentfield", "parenttype", "owner",
    "creation", "modified", "modified_by", "idx", "doctype",
})

# Fields that are always NPD-internal and must never be copied to production doctypes
_ALWAYS_EXCLUDE = frozenset({
    "name", "doctype", "owner", "creation", "modified", "modified_by",
    "modified_by_full_name", "idx", "__islocal", "naming_series",
    "is_promoted", "amended_from",
})


def strip_row_meta(rows):
    """Strip Frappe internal row metadata from a list of child-table row dicts."""
    if not rows:
        return []
    return [{k: v for k, v in row.items() if k not in _ROW_META_KEYS} for row in rows]


def build_promotion_data(npd_doc, target_doctype, extra_exclude=None,
                         field_remap=None, child_table_fields=None):
    """
    Build a clean dict from an NPD document, suitable for pre-filling a new
    production-doctype form via frappe.route_options.

    Args:
        npd_doc: Frappe Document instance (NPD doctype).
        target_doctype (str): The standard ERPNext doctype to promote into.
        extra_exclude (set): Additional fieldnames to exclude (doctype-specific).
        field_remap (dict): {npd_fieldname: target_fieldname} renames on copy.
        child_table_fields (list): Child table fieldnames to include.

    Returns:
        dict: Clean data dict with {"doctype": target_doctype, ...}
    """
    raw = npd_doc.as_dict()
    exclude = _ALWAYS_EXCLUDE | (extra_exclude or set())
    remap = field_remap or {}

    # Get the field names that actually exist on the target doctype
    target_meta_fields = {f.fieldname for f in frappe.get_meta(target_doctype).fields}

    result = {"doctype": target_doctype}

    for key, value in raw.items():
        if key in exclude or key.startswith("_"):
            continue
        target_key = remap.get(key, key)
        if target_key in target_meta_fields:
            result[target_key] = value

    # Handle child tables
    for table_field in (child_table_fields or []):
        target_table = remap.get(table_field, table_field)
        rows = raw.get(table_field)
        if rows:
            result[target_table] = strip_row_meta(rows)

    return result


class NpdPromotionMixin:
    """
    Mixin that provides a standard get_promotion_data + _post_promotion pattern
    for NPD Document classes.

    Subclasses must define:
        TARGET_DOCTYPE (str)      — e.g. "Item", "BOM", "Supplier"
        _NPD_EXTRA_EXCLUDE (set) — extra fields to exclude beyond defaults
        _CHILD_TABLE_FIELDS (list) — child table fieldnames to copy
        _LINKED_FIELD (str)       — field on self that stores the linked doc name
    """

    TARGET_DOCTYPE = None
    _NPD_EXTRA_EXCLUDE = set()
    _CHILD_TABLE_FIELDS = []
    _LINKED_FIELD = "linked_item"

    @staticmethod
    def default_get_promotion_data(npd_doctype, doc_name):
        """
        Generic static helper — call from each doctype's whitelisted static method.
        """
        npd = frappe.get_doc(npd_doctype, doc_name)
        if npd.get("is_promoted"):
            frappe.throw(f"{npd_doctype} <b>{doc_name}</b> has already been promoted to production.")
        return build_promotion_data(
            npd,
            npd.TARGET_DOCTYPE,
            extra_exclude=npd._NPD_EXTRA_EXCLUDE,
            child_table_fields=npd._CHILD_TABLE_FIELDS,
        )

    def _post_promotion(self, production_doc_name):
        """Mark this NPD document as promoted and link it to the created production doc."""
        self.is_promoted = 1
        self.set(self._LINKED_FIELD, production_doc_name)
        self.save(ignore_permissions=True)
