frappe.ui.form.on("Item", {
    setup: function(frm) {
        frm.set_query("npdi_default_nutritional_profile", function() {
            return {
                filters: {
                    docstatus: 1,
                    reference_doctype: "Item",
                    reference_name: frm.doc.name
                }
            };
        });
    },
    npdi_include_in_nutrient_calc: function(frm) {
        if (frm.doc.npdi_include_in_nutrient_calc && !frm.doc.stock_uom) {
            frm.set_value("stock_uom", "Kg");
            frappe.show_alert({
                message: __("Defaulted Stock UOM to Kg for nutritional calculations."),
                indicator: "green"
            });
        }
    }
});
