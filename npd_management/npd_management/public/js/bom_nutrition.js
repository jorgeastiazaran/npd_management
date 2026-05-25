frappe.ui.form.on("BOM", {
    onload: function(frm) {
        if (frm.doc.__islocal && frm.doc.items && frm.doc.items.length > 0) {
            setTimeout(() => frm.trigger("calculate_nutritional_info"), 500);
        }
    },
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

        
        let safe_items = (frm.doc.items || []).map(row => {
            return {
                item_code: row.item_code,
                item_doctype: row.item_doctype || "Item",
                stock_uom: row.stock_uom,
                include_in_nutrient_calc: row.include_in_nutrient_calc,
                weight_per_unit: row.weight_per_unit,
                weight_uom: row.weight_uom
            };
        });
        
        frappe.call({
            method: "npd_management.bom_nutrition.check_kg_conversions",
            args: { items_json: JSON.stringify(safe_items) },
            callback: function(r) {
                let missing = r.message || [];
                if (missing.length > 0) {
                    let fields = [
                        { fieldname: "help_html", fieldtype: "HTML", options: "<div class='text-muted'>" + __("The following items are missing a Kg conversion factor. Nutritional calculation requires a Kg conversion. Please confirm the conversion factors:") + "</div>" }
                    ];
                    
                    missing.forEach((item, idx) => {
                        fields.push({ fieldtype: "Section Break" });
                        fields.push({ fieldname: "item_html_" + idx, fieldtype: "HTML", options: "<b>" + item.item_code + "</b> (" + item.stock_uom + ")" });
                        fields.push({ fieldname: "conv_" + idx, fieldtype: "Float", label: __("1 Kg = [X] ") + item.stock_uom, reqd: 1, default: item.suggested_conversion || "" });
                    });
                    
                    let d = new frappe.ui.Dialog({
                        title: __("Missing Kg Conversions"),
                        fields: fields,
                        primary_action: function(values) {
                            let conversions = [];
                            missing.forEach((item, idx) => {
                                conversions.push({
                                    item_code: item.item_code,
                                    item_doctype: item.item_doctype,
                                    conversion_factor: values["conv_" + idx]
                                });
                            });
                            
                            frappe.call({
                                method: "npd_management.bom_nutrition.save_kg_conversions",
                                args: { conversions: JSON.stringify(conversions) },
                                freeze: true,
                                callback: function(r2) {
                                    d.hide();
                                    frm.trigger("_do_recalculate");
                                }
                            });
                        }
                    });
                    d.show();
                } else {
                    frm.trigger("_do_recalculate");
                }
            }
        });
    },
    _do_recalculate: function(frm) {
        let safe_items = (frm.doc.items || []).map(row => {
            return {
                item_code: row.item_code,
                item_doctype: row.item_doctype || "Item",
                qty: row.qty,
                stock_qty: row.stock_qty,
                conversion_factor: row.conversion_factor,
                include_in_nutrient_calc: row.include_in_nutrient_calc
            };
        });
        
        let safe_doc = {
            items: safe_items,
            npdi_reference_quantity_g: frm.doc.npdi_reference_quantity_g
        };

        frappe.call({
            method: "npd_management.bom_nutrition.calculate_nutrition_for_doc",
            args: { doc_json: JSON.stringify(safe_doc) },
            callback: function(r) {
                if (!r.exc && r.message) {
                    let totals = r.message.totals;
                    for (let key in totals) {
                        if (key === "total_yield_kg" && frm.fields_dict.npdi_total_yield_kg) {
                            frm.set_value("npdi_total_yield_kg", totals[key]);
                        } else if (frm.fields_dict[key]) {
                            frm.set_value(key, totals[key]);
                        }
                    }
                    if (r.message.warnings && r.message.warnings.length > 0) {
                        frappe.msgprint({
                            title: __('Reference Quantity Discrepancy'),
                            indicator: 'orange',
                            message: r.message.warnings.join('<br><br>')
                        });
                    }
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
