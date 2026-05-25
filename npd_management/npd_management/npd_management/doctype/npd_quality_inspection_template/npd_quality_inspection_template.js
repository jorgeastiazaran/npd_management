// Copyright (c) 2026, Tecnofood and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPD Quality Inspection Template', {
    refresh: function(frm) {
        // Promote to Quality Inspection Template button
        if (!frm.doc.__islocal && !frm.doc.is_promoted) {
            frm.add_custom_button(__("Promote to QI Template"), function() {
                npd_mgmt.open_promote_form(frm, {
                    target_doctype: "Quality Inspection Template",
                    api_method: "npd_management.npd_management.doctype.npd_quality_inspection_template.npd_quality_inspection_template.get_promotion_data",
                    confirm_msg: __("This will open a new <b>Quality Inspection Template</b> form pre-filled from <b>{0}</b>. Review and save to complete.", [frm.doc.name]),
                });
            }).addClass("btn-primary");
        }
    }
});
