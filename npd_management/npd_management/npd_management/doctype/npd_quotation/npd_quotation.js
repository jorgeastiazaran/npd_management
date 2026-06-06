// Copyright (c) 2026, Tecnofood and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPD Quotation', {
    refresh: function(frm) {
        // Gated pipeline button: visible only in Submitted state when unpromoted
        if (frm.doc.status === 'Submitted' && !frm.doc.is_promoted) {
            frm.add_custom_button(__('Promote to Sales Quotation'), function() {
                frappe.require("/assets/npd_management/js/npd_promotion.js", function() {
npd_mgmt.open_promote_form(frm, {
                    target_doctype: "Quotation",
                    api_method: "npd_management.npd_management.doctype.npd_quotation.npd_quotation.get_promotion_data",
                    confirm_msg: __("This will open a new <b>Sales Quotation</b> form pre-filled with data from <b>{0}</b>. All NPD Items must already be promoted. Review and save to complete.", [frm.doc.name]),
                });
                });
            }).addClass('btn-primary');
        }
    },
    
    quotation_to: function(frm) {
        frm.set_value('party_name', '');
        frm.set_value('customer_name', '');
        frm.set_value('lead_name', '');
    },
    
    party_name: function(frm) {
        if (frm.doc.party_name) {
            let field_to_fetch = frm.doc.quotation_to === 'Customer' ? 'customer_name' : 'lead_name';
            frappe.db.get_value(frm.doc.quotation_to, frm.doc.party_name, field_to_fetch)
                .then(r => {
                    if (r && r.message) {
                        frm.set_value(field_to_fetch, r.message[field_to_fetch]);
                    }
                });
        } else {
            frm.set_value('customer_name', '');
            frm.set_value('lead_name', '');
        }
    },
    
    tc_name: function(frm) {
        if (frm.doc.tc_name) {
            frappe.db.get_value("Terms and Conditions", frm.doc.tc_name, "terms")
                .then(r => {
                    if (r && r.message) {
                        frm.set_value("terms", r.message.terms);
                    }
                });
        }
    },
    
    taxes_and_charges: function(frm) {
        if (frm.doc.taxes_and_charges) {
            frappe.model.with_doc("Sales Taxes and Charges Template", frm.doc.taxes_and_charges, function() {
                let template = frappe.model.get_doc("Sales Taxes and Charges Template", frm.doc.taxes_and_charges);
                frm.clear_table("taxes");
                $.each(template.taxes || [], function(i, d) {
                    let row = frm.add_child("taxes");
                    row.charge_type = d.charge_type;
                    row.account_head = d.account_head;
                    row.description = d.description;
                    row.cost_center = d.cost_center;
                    row.rate = d.rate;
                    row.tax_amount = d.tax_amount;
                });
                frm.refresh_field("taxes");
            });
        }
    }
});

frappe.ui.form.on('NPD Quotation Item', {
    npd_item: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.npd_item) {
            frappe.call({
                method: "npd_management.npd_management.doctype.npd_quotation.npd_quotation.get_formula_estimated_cost",
                args: { npd_item: row.npd_item },
                callback: function(r) {
                    if (!r.exc && r.message !== undefined) {
                        frappe.model.set_value(cdt, cdn, 'estimated_cost', flt(r.message));
                        calculate_row_metrics(frm, cdt, cdn);
                    }
                }
            });
        }
    },
    
    qty: function(frm, cdt, cdn) {
        calculate_row_metrics(frm, cdt, cdn);
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_row_metrics(frm, cdt, cdn);
    },
    
    items_remove: function(frm) {
        frm.save(); // trigger server recalculation natively
    }
});

function calculate_row_metrics(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let amount = flt(row.qty) * flt(row.rate);
    frappe.model.set_value(cdt, cdn, 'amount', amount);
    
    let margin = 0.0;
    if (flt(row.rate) > 0) {
        margin = ((flt(row.rate) - flt(row.estimated_cost)) / flt(row.rate)) * 100.0;
    }
    frappe.model.set_value(cdt, cdn, 'gross_margin', margin);
    
    frm.refresh_field('items');
}
