# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class NPDQuotation(Document):
    def validate(self):
        self.calculate_totals()
        
    def calculate_totals(self):
        total_amount = 0.0
        total_cost = 0.0
        
        for item in self.get("items"):
            item.amount = flt(item.qty) * flt(item.rate)
            if flt(item.rate) > 0:
                item.gross_margin = ((flt(item.rate) - flt(item.estimated_cost)) / flt(item.rate)) * 100.0
            else:
                item.gross_margin = 0.0
                
            total_amount += item.amount
            total_cost += flt(item.estimated_cost) * flt(item.qty)
            
        self.total = total_amount
        self.total_estimated_cost = total_cost
        
        if total_amount > 0:
            self.overall_gross_margin = ((total_amount - total_cost) / total_amount) * 100.0
        else:
            self.overall_gross_margin = 0.0

    @frappe.whitelist()
    def promote_to_standard_quotation(self):
        """Atomically promotes the experimental NPD Quotation into a standard Sales Quotation."""
        if self.is_promoted:
            frappe.throw("This quotation has already been promoted to a standard Sales Quotation.")
            
        if self.status != "Approved":
            frappe.throw("Quotation status must be 'Approved' before executing final sales pipeline mapping.")
            
        if not self.get("items"):
            frappe.throw("Cannot promote an empty quotation. Please add experimental candidate formulation items.")
            
        # Enclose transaction in savepoint to guarantee atomic commit/rollback behavior
        try:
            frappe.db.savepoint("npd_qtn_promotion")
            
            # 1. Build standard Quotation payload
            qtn = frappe.new_doc("Quotation")
            qtn.quotation_to = self.quotation_to
            qtn.party_name = self.party_name
            qtn.transaction_date = self.transaction_date
            if self.valid_till:
                qtn.valid_till = self.valid_till
            qtn.currency = self.currency
            qtn.company = self.company
            qtn.order_type = "Sales"
            
            # 2. Map items with exact pricing preservation policy enforced
            for row in self.get("items"):
                npd_item_doc = frappe.get_doc("NPD Item", row.npd_item)
                if not npd_item_doc.linked_item:
                    frappe.throw(
                        f"Row #{row.idx}: Candidate item '{row.npd_item}' has not been promoted to stocking inventory yet. "
                        "All candidate items must be established in production inventory prior to pipeline bidding mapping."
                    )
                    
                qtn.append("items", {
                    "item_code": npd_item_doc.linked_item,
                    "qty": row.qty,
                    "rate": row.rate,
                    "uom": row.uom or npd_item_doc.stock_uom,
                    "description": row.description
                })
                
            # Insert standard document directly into database
            qtn.insert(ignore_permissions=True)
            
            # 3. Update tracking state natively
            self.is_promoted = 1
            self.promoted_quotation = qtn.name
            self.status = "Promoted"
            self.save(ignore_permissions=True)
            
            frappe.msgprint(f"Successfully mapped agreement metrics into live Sales Quotation: <b>{qtn.name}</b>")
            return qtn.name
            
        except Exception as e:
            frappe.db.rollback(save_point="npd_qtn_promotion")
            frappe.log_error(frappe.get_traceback(), "NPD Quotation Pipeline Mapping Error")
            frappe.throw(f"Promotion interlock aborted: {str(e)}")

@frappe.whitelist()
def get_formula_estimated_cost(npd_item):
    """Calculates custom candidate formula raw material costs dynamically from active R&D BOM layer."""
    if not npd_item:
        return 0.0
        
    # Attempt to locate linked experimental BOM candidates matching this item
    boms = frappe.get_all("BOM", filters={"item": npd_item, "is_npd_bom": 1, "docstatus": 1}, fields=["name", "total_cost"], order_by="modified desc", limit=1)
    if boms:
        return flt(boms[0].total_cost)
        
    # Fallback check standard/draft BOMs
    draft_boms = frappe.get_all("BOM", filters={"item": npd_item, "is_npd_bom": 1}, fields=["name", "total_cost"], order_by="modified desc", limit=1)
    if draft_boms:
        return flt(draft_boms[0].total_cost)
        
    # Final fallback check if NPD Item itself stores custom target base pricing
    item_doc = frappe.get_doc("NPD Item", npd_item)
    return flt(item_doc.get("valuation_rate")) or flt(item_doc.get("standard_rate")) or 0.0
