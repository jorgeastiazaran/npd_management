frappe.ui.form.on("NPD Supplier Quotation", {
    refresh: function(frm) {
        if (!frm.doc.is_promoted && frm.doc.docstatus !== 2) {
            frm.add_custom_button(__("Promote to Supplier Quotation"), function() {
                frappe.confirm(
                    __("Are you sure you want to promote this to a standard Supplier Quotation?"),
                    () => {
                        frm.call("promote_to_production").then(() => frm.reload_doc());
                    }
                );
            }, __("Actions"));
        }
    }
});
