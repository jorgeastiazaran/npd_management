frappe.ui.form.on("NPD RFQ", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create NPD Supplier Quotation"), function() {
                frappe.call({
                    method: "npd_management.npd_management.doctype.npd_rfq.npd_rfq.create_supplier_quotation",
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
