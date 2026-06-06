// Copyright (c) 2025, NPD Management
frappe.ui.form.on('NPD Supplier', {
    onload: function(frm) {
        frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'NPD Supplier'};
        if (!frm.is_new()) {
            try {
                frappe.contacts.setup_contact(frm);
                frappe.contacts.setup_address(frm);
            } catch(e) {
                console.warn(e);
            }
        }
    },
    refresh(frm) {
        frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'NPD Supplier'};
        
        if (!frm.is_new()) {
            try {
                frappe.contacts.setup_contact(frm);
                frappe.contacts.setup_address(frm);
            } catch(e) {
                console.warn(e);
            }
            if (!frm.doc.is_promoted && frm.doc.evaluation_status === 'Approved') {
                frm.add_custom_button(__('Promote to Supplier'), function() {
                    frappe.confirm(
                        __('Promote this NPD Supplier to a live ERPNext Supplier? This will also promote any eligible NPD Supplier Quotations.'),
                        function() {
                            frappe.require("/assets/npd_management/js/npd_promotion.js", function() {
npd_mgmt.open_promote_form(frm, {
                        target_doctype: "Supplier",
                        api_method: "npd_management.npd_management.doctype.npd_supplier.npd_supplier.get_promotion_data",
                    });
                });
                        }
                    );
                }, __('NPD Actions'));
            }

            if (frm.doc.is_promoted && frm.doc.linked_supplier) {
                frm.add_custom_button(__('View Supplier'), function() {
                    frappe.set_route('Form', 'Supplier', frm.doc.linked_supplier);
                }, __('NPD Actions'));
            }
        }
    },
    supplier_primary_address: function(frm) {
        if (frm.doc.supplier_primary_address) {
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: {
                    address_dict: frm.doc.supplier_primary_address
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("primary_address", r.message);
                    }
                }
            });
        } else {
            frm.set_value("primary_address", "");
        }
    }
});
