frappe.ui.form.on("NPD Item", {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            // New doc: show series picker, hide item_code (server fills it via before_insert)
            frm.toggle_display("naming_series", true);
            frm.toggle_display("item_code", false);
        } else {
            // Saved doc: hide series picker, show item_code read-only
            frm.toggle_display("naming_series", false);
            frm.toggle_display("item_code", true);
            frm.set_df_property("item_code", "read_only", true);
            
            if (!frm.doc.is_promoted) {
                frm.add_custom_button(__("Promote to Item"), function() {
                    frappe.confirm(
                        __("This will create a new ERPNext Item from NPD Item <b>{0}</b> and open its full form for review before saving. Continue?", [frm.doc.name]),
                        function() {
                            frappe.show_progress(__("Preparing Item..."), 30, 100);
                            frappe.call({
                                method: "npd_management.npd_management.doctype.npd_item.npd_item.get_promotion_data",
                                args: { npd_item_name: frm.doc.name },
                                callback: function(r) {
                                    frappe.hide_progress();
                                    if (r.exc) return;
                                    let item_data = r.message;
                                    frappe.new_doc("Item", item_data);
                                }
                            });
                        }
                    );
                }).addClass("btn-primary");
            }

            // ── Nutritional Profile button ─────────────────────────────────────
            frm.add_custom_button(__("Manage Nutritional Profile"), function() {
                // Check if there's an existing profile for this item
                frappe.db.get_list("Nutritional Profile", {
                    filters: { reference_doctype: "NPD Item", reference_name: frm.doc.name },
                    limit: 1,
                    fields: ["name"]
                }).then(function(existing) {
                    if (existing && existing.length > 0) {
                        // Open list filtered to this item
                        frappe.set_route("List", "Nutritional Profile", {
                            reference_doctype: "NPD Item",
                            reference_name: frm.doc.name
                        });
                    } else {
                        // Create a new profile pre-filled with this item
                        frappe.new_doc("Nutritional Profile", {
                            reference_doctype: "NPD Item",
                            reference_name: frm.doc.name,
                            is_default: 1
                        });
                    }
                });
            }, __("Nutritional"));
        }
    },
    setup: function(frm) {
        frm.set_query("npdi_default_nutritional_profile", function() {
            return {
                filters: {
                    docstatus: 1,
                    reference_doctype: "NPD Item",
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

