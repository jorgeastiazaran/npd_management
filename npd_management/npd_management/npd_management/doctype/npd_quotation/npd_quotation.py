# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.stock.get_item_details import get_item_details

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

    def before_submit(self):
        self.status = "Submitted"


    @frappe.whitelist()
    @staticmethod
    def get_promotion_data(npd_item_name):
        """Returns a clean dict mapped to the standard Quotation doctype for full-form promotion."""
        npd = frappe.get_doc("NPD Quotation", npd_item_name)
        if npd.is_promoted:
            frappe.throw(f"NPD Quotation <b>{npd_item_name}</b> has already been promoted.")
        if npd.status != "Submitted":
            frappe.throw("Quotation status must be 'Submitted' before promoting.")
        if not npd.get("items"):
            frappe.throw("Cannot promote an empty quotation.")

        items = []
        taxes = []
        for row in npd.get("items"):
            npd_item_doc = frappe.get_doc("NPD Item", row.npd_item)
            if not npd_item_doc.linked_item:
                frappe.throw(
                    f"Row #{row.idx}: NPD Item <b>{row.npd_item}</b> must be promoted to an Item first."
                )
            item_args = frappe._dict({
                "item_code": npd_item_doc.linked_item,
                "company": npd.company,
                "qty": row.qty,
                "customer": npd.party_name if npd.quotation_to == "Customer" else None,
                "doctype": "Quotation",
                "name": npd.name,
                "price_list": npd.selling_price_list,
                "currency": npd.currency,
                "conversion_rate": npd.conversion_rate or 1.0,
                "price_list_currency": npd.price_list_currency,
                "plc_conversion_rate": npd.plc_conversion_rate or 1.0,
                "transaction_date": npd.transaction_date,
            })
            
            try:
                details = get_item_details(item_args)
            except Exception:
                details = {}
                
            mapped_row = details.copy()
            for key in ["doctype", "name", "parent", "parenttype", "parentfield", "idx"]:
                mapped_row.pop(key, None)
            mapped_row.update({
                "item_code": npd_item_doc.linked_item,
                "item_name": details.get("item_name") or npd_item_doc.linked_item,
                "qty": row.qty,
                "rate": row.rate,
                "price_list_rate": row.price_list_rate,
                "discount_percentage": row.discount_percentage,
                "uom": row.uom or npd_item_doc.stock_uom or details.get("uom"),
                "description": row.description or details.get("description", ""),
            })
            items.append(mapped_row)

        for row in npd.get("taxes"):
            taxes.append({
                "charge_type": row.charge_type,
                "account_head": row.account_head,
                "description": row.description,
                "cost_center": row.cost_center,
                "rate": row.rate,
                "tax_amount": row.tax_amount,
            })

        return {
            "doctype": "Quotation",
            "quotation_to": npd.quotation_to,
            "party_name": npd.party_name,
            "project": npd.project,
            "transaction_date": str(npd.transaction_date) if npd.transaction_date else None,
            "valid_till": str(npd.valid_till) if npd.valid_till else None,
            "selling_price_list": npd.selling_price_list,
            "price_list_currency": npd.price_list_currency,
            "plc_conversion_rate": npd.plc_conversion_rate,
            "currency": npd.currency,
            "conversion_rate": npd.conversion_rate,
            "additional_discount_percentage": npd.additional_discount_percentage,
            "taxes_and_charges": npd.taxes_and_charges,
            "tc_name": npd.tc_name,
            "terms": npd.terms,
            "company": npd.company,
            "order_type": "Sales",
            "items": items,
            "taxes": taxes,
            "custom_npd_quotation_reference": npd.name,
        }

    @frappe.whitelist()
    def promote_to_standard_quotation(self):
        """Atomically promotes the experimental NPD Quotation into a standard Sales Quotation."""
        if self.is_promoted:
            frappe.throw("This quotation has already been promoted to a standard Sales Quotation.")
            
        if self.status != "Submitted":
            frappe.throw("Quotation status must be 'Submitted' before executing final sales pipeline mapping.")
            
        if not self.get("items"):
            frappe.throw("Cannot promote an empty quotation. Please add experimental candidate formulation items.")
            
        # Enclose transaction in savepoint to guarantee atomic commit/rollback behavior
        try:
            frappe.db.savepoint("npd_qtn_promotion")
            
            # 1. Build standard Quotation payload
            qtn = frappe.new_doc("Quotation")
            qtn.quotation_to = self.quotation_to
            qtn.party_name = self.party_name
            qtn.project = self.project
            qtn.transaction_date = self.transaction_date
            if self.valid_till:
                qtn.valid_till = self.valid_till
            qtn.selling_price_list = self.selling_price_list
            qtn.price_list_currency = self.price_list_currency
            qtn.plc_conversion_rate = self.plc_conversion_rate
            qtn.currency = self.currency
            qtn.conversion_rate = self.conversion_rate
            qtn.additional_discount_percentage = self.additional_discount_percentage
            qtn.taxes_and_charges = self.taxes_and_charges
            qtn.tc_name = self.tc_name
            qtn.terms = self.terms
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
                    
                item_args = frappe._dict({
                    "item_code": npd_item_doc.linked_item,
                    "company": self.company,
                    "qty": row.qty,
                    "customer": self.party_name if self.quotation_to == "Customer" else None,
                    "doctype": "Quotation",
                    "name": self.name,
                    "price_list": self.selling_price_list,
                    "currency": self.currency,
                    "conversion_rate": self.conversion_rate or 1.0,
                    "price_list_currency": self.price_list_currency,
                    "plc_conversion_rate": self.plc_conversion_rate or 1.0,
                    "transaction_date": self.transaction_date,
                })
                
                try:
                    details = get_item_details(item_args)
                except Exception:
                    details = {}
                    
                mapped_row = details.copy()
                for key in ["doctype", "name", "parent", "parenttype", "parentfield", "idx"]:
                    mapped_row.pop(key, None)
                mapped_row.update({
                    "item_code": npd_item_doc.linked_item,
                    "item_name": details.get("item_name") or npd_item_doc.linked_item,
                    "qty": row.qty,
                    "rate": row.rate,
                    "price_list_rate": row.price_list_rate,
                    "discount_percentage": row.discount_percentage,
                    "uom": row.uom or npd_item_doc.stock_uom or details.get("uom"),
                    "description": row.description or details.get("description", "")
                })
                qtn.append("items", mapped_row)
                
            for row in self.get("taxes"):
                qtn.append("taxes", {
                    "charge_type": row.charge_type,
                    "account_head": row.account_head,
                    "description": row.description,
                    "cost_center": row.cost_center,
                    "rate": row.rate,
                    "tax_amount": row.tax_amount,
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
    boms = frappe.get_all("NPD BOM", filters={"item": npd_item, "docstatus": 1}, fields=["name", "total_cost"], order_by="modified desc", limit=1)
    if boms:
        return flt(boms[0].total_cost)
        
    # Fallback check standard/draft BOMs
    draft_boms = frappe.get_all("NPD BOM", filters={"item": npd_item}, fields=["name", "total_cost"], order_by="modified desc", limit=1)
    if draft_boms:
        return flt(draft_boms[0].total_cost)
        
    # Final fallback check if NPD Item itself stores custom target base pricing
    item_doc = frappe.get_doc("NPD Item", npd_item)
    return flt(item_doc.get("valuation_rate")) or flt(item_doc.get("standard_rate")) or 0.0


# Expose the static method at the module level for frappe.call route
get_promotion_data = NPDQuotation.get_promotion_data
