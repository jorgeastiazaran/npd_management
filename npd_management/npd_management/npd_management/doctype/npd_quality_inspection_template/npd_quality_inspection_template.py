# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

class NPDQualityInspectionTemplate(Document):
    @frappe.whitelist()
    @staticmethod
    def get_promotion_data(npd_item_name):
        """Returns a clean dict mapped to Quality Inspection Template for full-form promotion."""
        from npd_management.api.npd_promotion import build_promotion_data
        npd = frappe.get_doc("NPD Quality Inspection Template", npd_item_name)
        if npd.get("is_promoted"):
            frappe.throw(f"NPD Quality Inspection Template <b>{npd_item_name}</b> has already been promoted.")
        _EXCLUDE = {"is_promoted", "linked_qi_template"}
        data = build_promotion_data(npd, "Quality Inspection Template",
                                    extra_exclude=_EXCLUDE,
                                    child_table_fields=["item_quality_inspection_parameter"])
        data["custom_npd_qi_template_reference"] = npd.name
        return data
