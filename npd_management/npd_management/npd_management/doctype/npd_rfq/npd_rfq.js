frappe.ui.form.on("NPD RFQ", {
    refresh: function(frm) {
        // Promote to RFQ button
        if (!frm.doc.__islocal && frm.doc.docstatus === 1 && !frm.doc.is_promoted) {
            frm.add_custom_button(__("Promote to RFQ"), function() {
                npd_mgmt.open_promote_form(frm, {
                    target_doctype: "Request for Quotation",
                    api_method: "npd_management.npd_management.npd_management.doctype.npd_rfq.npd_rfq.get_promotion_data",
                    confirm_msg: __("This will open a new <b>Request for Quotation</b> form pre-filled from <b>{0}</b>. Review and save to complete.", [frm.doc.name]),
                });
            }).addClass("btn-primary");
        }

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create NPD Supplier Quotation"), function() {
                frappe.call({
                    method: "npd_management.doctype.npd_rfq.npd_rfq.create_supplier_quotation",
                    args: { rfq: frm.doc.name },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route("Form", "NPD Supplier Quotation", r.message);
                        }
                    }
                });
            }, __("Actions"));
        }
    }
});
