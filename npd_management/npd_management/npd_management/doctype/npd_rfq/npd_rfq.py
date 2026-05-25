# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document


class NPDRFQ(Document):
    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    @frappe.whitelist()
    def create_npd_supplier_quotations(self):
        """Creates one NPD Supplier Quotation per supplier in this NPD RFQ."""
        if self.docstatus != 1:
            frappe.throw("Please submit the NPD RFQ before creating quotations.")

        created = []
        for supplier_row in self.suppliers:
            # Build items list
            items = []
            for item in self.items:
                items.append({
                    "item_type": item.item_type,
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "warehouse": item.warehouse,
                    "project": item.project,
                    "schedule_date": item.schedule_date or self.schedule_date,
                    "rate": 0,
                })

            sq = frappe.get_doc({
                "doctype": "NPD Supplier Quotation",
                "supplier_type": supplier_row.supplier_type,
                "supplier": supplier_row.supplier,
                "company": self.company,
                "transaction_date": frappe.utils.nowdate(),
                "currency": frappe.get_cached_value("Company", self.company, "default_currency") or "MXN",
                "conversion_rate": 1,
                "npd_rfq": self.name,
                "items": items,
                "status": "",
            })
            sq.insert(ignore_permissions=True)
            created.append(sq.name)

        frappe.db.commit()

        if created:
            frappe.msgprint(
                f"Created {len(created)} NPD Supplier Quotation(s): <b>{', '.join(created)}</b>",
                alert=True
            )
        else:
            frappe.msgprint("No suppliers found to create quotations for.", alert=True)

        return created
