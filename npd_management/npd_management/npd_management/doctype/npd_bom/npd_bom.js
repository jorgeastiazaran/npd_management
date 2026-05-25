frappe.ui.form.on("NPD BOM", {
    setup: function(frm) {
        console.log("NPD BOM Script Loaded");
    },
    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.docstatus === 1 && !frm.doc.is_promoted) {
            frm.add_custom_button(__("Promote to BOM"), function() {
                npd_mgmt.open_promote_form(frm, {
                    target_doctype: "BOM",
                    api_method: "npd_management.doctype.npd_bom.npd_bom.get_promotion_data",
                    confirm_msg: __("This will open a new <b>BOM</b> form pre-filled with data from <b>{0}</b>. Review and save to complete the promotion.", [frm.doc.name]),
                });
            }).addClass("btn-primary");
        }
    },
    item_doctype: function(frm) {
        // Clear main item when parent type changes
        frm.set_value("item", "");
    },
    default_item_doctype: function(frm) {
        // Bulk update child rows to match the table's Default Item Type
        if (frm.doc.default_item_doctype && frm.doc.items && frm.doc.items.length > 0) {
            frappe.confirm(
                __("Update Item Type for all rows in the Items table to '{0}'?", [frm.doc.default_item_doctype]),
                () => {
                    frm.doc.items.forEach(function(row) {
                        frappe.model.set_value(row.doctype, row.name, "item_doctype", frm.doc.default_item_doctype);
                        frappe.model.set_value(row.doctype, row.name, "item_code", "");
                    });
                    frm.refresh_field("items");
                    frappe.show_alert({
                        message: __("Updated all rows to: {0}", [frm.doc.default_item_doctype]),
                        indicator: "green"
                    });
                }
            );
        }
    },
    calculate_nutritional_info: function(frm) {
        if (!frm.doc.items || frm.doc.items.length === 0) return;
        
        // Step 1: Check for missing Kg conversions
        frappe.call({
            method: "check_kg_conversions",
            doc: frm.doc,
            args: { items_json: JSON.stringify(frm.doc.items) },
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
                                method: "save_kg_conversions",
                                doc: frm.doc,
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
        frm.call({
            method: "calculate_nutritional_info",
            doc: frm.doc,
            callback: function(r) {
                if (r.message && r.message.warnings && r.message.warnings.length > 0) {
                    frappe.msgprint({
                        title: __('Reference Quantity Discrepancy'),
                        indicator: 'orange',
                        message: r.message.warnings.join('<br><br>')
                    });
                }
                frm.refresh_fields();
            }
        });
    },
    rm_cost_as_per: function(frm) {
        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.call({
                method: "calculate_cost",
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        // Update child row rates/amounts
                        if (r.message.items) {
                            r.message.items.forEach((item_data, i) => {
                                let row = frm.doc.items[i];
                                if (row) {
                                    $.extend(row, item_data);
                                }
                            });
                        }
                        // Update totals
                        frm.set_value("total_cost", r.message.total_cost);
                        frm.set_value("base_total_cost", r.message.base_total_cost);
                        frm.set_value("raw_material_cost", r.message.raw_material_cost);
                        frm.set_value("base_raw_material_cost", r.message.base_raw_material_cost);
                        
                        frm.refresh_fields();
                    }
                }
            });
        }
    }
});

frappe.ui.form.on("NPD BOM Item", {
    items_add: function(frm, cdt, cdn) {
        // New row inherits default Item Type for table
        if (frm.doc.default_item_doctype) {
            frappe.model.set_value(cdt, cdn, "item_doctype", frm.doc.default_item_doctype);
        }
    },
    qty: function(frm, cdt, cdn) {
        frm.trigger("calculate_nutritional_info");
    },
    has_nutritional_content: function(frm, cdt, cdn) {
        frm.trigger("calculate_nutritional_info");
    },
    include_in_nutrient_calc: function(frm) {
        frm.trigger("calculate_nutritional_info");
    },
    uom: function(frm) {
        frm.trigger("calculate_nutritional_info");
    },
    item_doctype: function(frm, cdt, cdn) {
        // Clear item when type changes in a row
        frappe.model.set_value(cdt, cdn, "item_code", "");
    },
    item_code: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (!d.item_code) return;
        
        console.log("Fetching details for:", d.item_code);

        return frappe.call({
            doc: frm.doc,
            method: "get_bom_material_detail",
            args: {
                item_code: d.item_code,
                item_doctype: d.item_doctype || frm.doc.default_item_doctype || "NPD Item",
                qty: d.qty || 1,
                uom: d.uom,
                stock_uom: d.stock_uom
            },
            callback: function(r) {
                console.log("Server response:", r);
                if (r.message) {
                    d = locals[cdt][cdn];
                    $.extend(d, r.message);
                    frm.refresh_field("items");
                    frm.trigger("calculate_nutritional_info");
                }
            },
            freeze: true
        });
    }
});
