frappe.ui.form.on("BOM", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0 && !frm.doc.nutritional_snapshot_locked) {
            frm.add_custom_button(__("Calculate Nutritional Info"), function() {
                frappe.call({
                    method: "npd_management.bom_nutrition.recalculate_bom_nutrition",
                    args: { bom_name: frm.doc.name },
                    freeze: true,
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });
            }, __("Nutritional"));
        }
        if (frm.doc.nutritional_snapshot_locked) {
            frm.dashboard.set_headline_alert(
                __("Nutritional values are locked (BOM submitted)."),
                "orange"
            );
        }
    },
    calculate_nutritional_info: function(frm) {
        if (frm.doc.nutritional_snapshot_locked || !frm.doc.items || !frm.doc.items.length) {
            return;
        }
        if (frm.doc.__islocal) {
            return;
        }
        frappe.call({
            method: "npd_management.bom_nutrition.recalculate_bom_nutrition",
            args: { bom_name: frm.doc.name },
            callback: function(r) {
                if (!r.exc) {
                    frm.reload_doc();
                }
            }
        });
    }
});

frappe.ui.form.on("BOM Item", {
    qty: function(frm) {
        frm.trigger("calculate_nutritional_info");
    },
    uom: function(frm) {
        frm.trigger("calculate_nutritional_info");
    },
    item_code: function(frm) {
        frm.trigger("calculate_nutritional_info");
    },
    include_in_nutrient_calc: function(frm) {
        frm.trigger("calculate_nutritional_info");
    }
});
