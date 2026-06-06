# -*- coding: utf-8 -*-
from frappe.model.document import Document
import frappe
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address

class NPDSupplier(Document):
    def onload(self):
        load_address_and_contact(self)

    def on_trash(self):
        delete_contact_and_address("NPD Supplier", self.name)

    def validate(self):
        if self.is_promoted and not self.linked_supplier:
            frappe.throw("Linked Supplier is required when is_promoted is set.")

    @frappe.whitelist()

    @frappe.whitelist()
    @staticmethod
    def get_promotion_data(npd_item_name):
        """Returns a clean dict mapped to the standard Supplier doctype for full-form promotion."""
        from npd_management.api.npd_promotion import build_promotion_data
        npd = frappe.get_doc("NPD Supplier", npd_item_name)
        if npd.is_promoted:
            frappe.throw(f"NPD Supplier <b>{npd_item_name}</b> has already been promoted.")
        if npd.evaluation_status != "Approved":
            frappe.throw("Only Approved NPD Suppliers can be promoted.")
        _EXCLUDE = {"is_promoted", "linked_supplier", "evaluation_status", "npd_notes"}
        data = build_promotion_data(npd, "Supplier", extra_exclude=_EXCLUDE, child_table_fields=["accounts"])
        data["custom_npd_supplier_reference"] = npd.name
        return data



# Expose the static method at the module level for frappe.call route
get_promotion_data = NPDSupplier.get_promotion_data
