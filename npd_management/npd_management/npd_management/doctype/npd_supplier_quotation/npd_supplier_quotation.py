# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document


class NPDSupplierQuotation(Document):
    def validate(self):
        self._calculate_totals()

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    def _calculate_totals(self):
        """Calculate net total and grand total from items."""
        total = 0
        for item in self.items:
            item.amount = (item.qty or 0) * (item.rate or 0)
            item.base_rate = (item.rate or 0) * (self.conversion_rate or 1)
            item.base_amount = item.amount * (self.conversion_rate or 1)
            total += item.amount
        self.total = total
        self.grand_total = total + (self.total_taxes_and_charges or 0)
        self.base_grand_total = self.grand_total * (self.conversion_rate or 1)

    def _all_items_promoted(self):
        """Returns True if all items are either standard Items or promoted NPD Items."""
        for item in self.items:
            if item.item_type == "NPD Item":
                is_promoted = frappe.db.get_value("NPD Item", item.item_code, "is_promoted")
                if not is_promoted:
                    return False
        return True

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes this NPD Supplier Quotation to a standard Supplier Quotation.
        - If supplier_type == 'NPD Supplier': supplier must be promoted first.
        - All NPD Items in the quotation must be promoted to Items.
        """
        if self.is_promoted:
            frappe.throw("This quotation has already been promoted.")

        if self.docstatus != 1:
            frappe.throw("Please submit the NPD Supplier Quotation before promoting.")

        # Resolve supplier
        if self.supplier_type == "NPD Supplier":
            linked_supplier = frappe.db.get_value("NPD Supplier", self.supplier, "linked_supplier")
            if not linked_supplier:
                frappe.throw(
                    f"NPD Supplier <b>{self.supplier}</b> must be promoted to a Supplier first."
                )
        else:
            linked_supplier = self.supplier

        # Check all items
        if not self._all_items_promoted():
            unready = []
            for item in self.items:
                if item.item_type == "NPD Item":
                    if not frappe.db.get_value("NPD Item", item.item_code, "is_promoted"):
                        unready.append(item.item_code)
            frappe.throw(
                f"The following NPD Items must be promoted before this quotation can be promoted: "
                f"<b>{', '.join(unready)}</b>"
            )

        self._do_promote(linked_supplier_name=linked_supplier, supplier_type="Supplier")

    def _do_promote(self, linked_supplier_name, supplier_type="Supplier"):
        """Internal: builds and inserts the ERPNext Supplier Quotation."""
        items = []
        for item in self.items:
            item_code = item.item_code
            if item.item_type == "NPD Item":
                item_code = frappe.db.get_value("NPD Item", item.item_code, "linked_item")

            items.append({
                "item_code": item_code,
                "item_name": item.item_name,
                "description": item.description or item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "stock_uom": item.stock_uom or item.uom,
                "conversion_factor": item.conversion_factor or 1,
                "rate": item.rate,
                "amount": item.amount,
                "base_rate": item.base_rate or item.rate,
                "base_amount": item.base_amount or item.amount,
                "warehouse": item.warehouse,
                "project": item.project,
                "lead_time_days": item.lead_time_days or 0,
            })

        sq_data = {
            "doctype": "Supplier Quotation",
            "supplier": linked_supplier_name,
            "company": self.company,
            "transaction_date": self.transaction_date,
            "valid_till": self.valid_till,
            "quotation_number": self.quotation_number,
            "currency": self.currency,
            "conversion_rate": self.conversion_rate or 1,
            "buying_price_list": self.buying_price_list,
            "items": items,
        }

        sq_doc = frappe.get_doc(sq_data)
        sq_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        self.is_promoted = 1
        self.linked_sq = sq_doc.name
        self.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(
            f"Supplier Quotation <b>{sq_doc.name}</b> created successfully.",
            alert=True
        )
