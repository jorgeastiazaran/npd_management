// Copyright (c) 2026, Tecnofood and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPD Quotation', {
    refresh: function(frm) {
        // Gated pipeline button: visible only in Approved state when unpromoted
        if (frm.doc.status === 'Approved' && !frm.doc.is_promoted) {
            frm.add_custom_button(__('Promote to Sales Quotation'), function() {
                frappe.confirm(
                    __('Are you sure you want to map this agreement into a live ERPNext Sales Quotation?<br><br><b>Interlock Rule:</b> Every experimental candidate formulation item must already be established in active production inventory.'),
                    function() {
                        frappe.call({
                            method: 'promote_to_standard_quotation',
                            doc: frm.doc,
                            freeze: true,
                            freeze_message: __('Mapping agreement metrics to live Sales Quotation...'),
                            callback: function(r) {
                                if (!r.exc && r.message) {
                                    frm.reload_doc();
                                    // Instantly redirect desktop view to newly created live document
                                    frappe.set_route('Form', 'Quotation', r.message);
                                }
                            }
                        });
                    }
                );
            }).addClass('btn-primary');
        }
    },
    
    quotation_to: function(frm) {
        frm.set_value('party_name', '');
    }
});

frappe.ui.form.on('NPD Quotation Item', {
    npd_item: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.npd_item) {
            frappe.call({
                method: 'npd_management.npd_management.doctype.npd_quotation.npd_quotation.get_formula_estimated_cost',
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
