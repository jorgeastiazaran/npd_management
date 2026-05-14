# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from npd_management.api.npd_utils import push_to_erpnext

class NPDItem(Document):
    def before_insert(self):
        # When using naming_series:, Frappe generates the name first.
        # We then copy it to item_code.
        if not self.item_code:
            self.item_code = self.name
        print(f"DEBUG: NPD Item Name: {self.name}, Item Code: {self.item_code}")

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes the NPD Item to a real Item in ERPNext."""
        if self.is_promoted:
            frappe.throw("This item has already been promoted to production.")
            
        # Map fields from NPD Item to standard ERPNext Item
        # Since we mirrored the structure, we can exclude NPD-specific fields
        doc_data = self.as_dict()
        exclude_fields = ["name", "is_promoted", "linked_item", "doctype", "owner", "creation", "modified", "modified_by"]
        for field in exclude_fields:
            if field in doc_data:
                del doc_data[field]
        
        # Add custom link back to NPD
        doc_data["custom_npd_reference"] = self.name
        
        # Ensure mandatory item_code is present for legacy NPD items created before auto-naming scripts
        if not doc_data.get("item_code"):
            doc_data["item_code"] = self.name
        
        try:
            response = push_to_erpnext("Item", doc_data)
            if response and response.get("name"):
                self.is_promoted = 1
                self.linked_item = response["name"]
                if not self.item_code:
                    self.item_code = self.linked_item
                self.save()
                frappe.msgprint(f"Successfully created Item {self.linked_item} in ERPNext.")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "NPD Promotion Error")
            frappe.throw(f"Failed to promote to ERPNext: {str(e)}")
