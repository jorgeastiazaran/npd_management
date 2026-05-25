frappe.ui.form.on("NPD Supplier Quotation", {
    refresh: function(frm) {
        if (!frm.doc.is_promoted && frm.doc.docstatus !== 2) {
            frm.add_custom_button(__("Promote to Supplier Quotation"), function() {
                frappe.confirm(
                    __("Are you sure you want to promote this to a standard Supplier Quotation?"),
                    () => {
                        npd_mgmt.open_promote_form(frm, {
                        target_doctype: "Supplier Quotation",
                        api_method: "npd_management.doctype.npd_supplier_quotation.npd_supplier_quotation.get_promotion_data",
                    }) => frm.reload_doc());
                    }
                );
            }, __("Actions"));
        }
    }
});
