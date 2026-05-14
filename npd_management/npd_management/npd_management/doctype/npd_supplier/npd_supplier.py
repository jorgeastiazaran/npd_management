# -*- coding: utf-8 -*-
from frappe.model.document import Document
import frappe


class NPDSupplier(Document):
    def validate(self):
        if self.is_promoted and not self.linked_supplier:
            frappe.throw("Linked Supplier is required when is_promoted is set.")

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes the NPD Supplier to a real Supplier in ERPNext.
        Also promotes any eligible NPD Supplier Quotations."""
        if self.is_promoted:
            frappe.throw("This supplier has already been promoted to production.")

        if self.evaluation_status != "Approved":
            frappe.throw("Supplier must have Evaluation Status 'Approved' before promotion.")

        # Build Supplier doc from NPD Supplier fields
        # Fields that map directly to Supplier
        supplier_fields = [
            "supplier_name", "supplier_group", "supplier_type", "country", "tax_id",
            "tax_category", "tax_withholding_category", "is_transporter", "is_internal_supplier",
            "represents_company", "default_currency", "default_price_list", "payment_terms",
            "on_hold", "hold_type", "release_date", "website", "supplier_details",
            "pan", "language", "is_frozen", "warn_rfqs", "warn_pos", "prevent_rfqs", "prevent_pos"
        ]

        supplier_data = {"doctype": "Supplier"}
        for field in supplier_fields:
            val = self.get(field)
            if val is not None:
                supplier_data[field] = val

        try:
            supplier_doc = frappe.get_doc(supplier_data)
            supplier_doc.insert(ignore_permissions=True)
            frappe.db.commit()

            self.is_promoted = 1
            self.linked_supplier = supplier_doc.name
            self.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(
                f"Supplier <b>{supplier_doc.name}</b> created successfully.<br>"
                "Attempting to promote eligible NPD Supplier Quotations...",
                alert=True
            )

            # Cascade: promote eligible NPD Supplier Quotations
            self._promote_eligible_quotations(supplier_doc.name)

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "NPD Supplier Promotion Error")
            frappe.throw(f"Failed to promote NPD Supplier: {str(e)}")

    def _promote_eligible_quotations(self, linked_supplier_name):
        """Promote NPD Supplier Quotations linked to this NPD Supplier that have all items promoted."""
        npd_sqs = frappe.get_all(
            "NPD Supplier Quotation",
            filters={
                "supplier_type": "NPD Supplier",
                "supplier": self.name,
                "is_promoted": 0,
                "docstatus": ["!=", 2]
            },
            fields=["name"]
        )

        promoted = []
        skipped = []

        for sq_meta in npd_sqs:
            sq = frappe.get_doc("NPD Supplier Quotation", sq_meta.name)
            all_promoted = sq._all_items_promoted()
            if all_promoted:
                try:
                    sq._do_promote(linked_supplier_name=linked_supplier_name, supplier_type="Supplier")
                    promoted.append(sq.name)
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(), f"Auto-promote SQ {sq.name} failed")
                    skipped.append(f"{sq.name} (error: {str(e)[:60]})")
            else:
                skipped.append(f"{sq.name} (unpromoted items)")

        if promoted:
            frappe.msgprint(f"Auto-promoted Supplier Quotations: {', '.join(promoted)}", alert=True)
        if skipped:
            frappe.msgprint(f"Skipped Supplier Quotations: {', '.join(skipped)}", alert=True)
