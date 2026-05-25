// Copyright (c) 2025, NPD Management
frappe.ui.form.on('NPD Supplier', {
    refresh(frm) {
        if (!frm.is_new()) {
            if (!frm.doc.is_promoted && frm.doc.evaluation_status === 'Approved') {
                frm.add_custom_button(__('Promote to Supplier'), function() {
                    frappe.confirm(
                        __('Promote this NPD Supplier to a live ERPNext Supplier? This will also promote any eligible NPD Supplier Quotations.'),
                        function() {
                            npd_mgmt.open_promote_form(frm, {
                        target_doctype: "Supplier",
                        api_method: "npd_management.npd_management.doctype.npd_supplier.npd_supplier.get_promotion_data",
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
    }
});
