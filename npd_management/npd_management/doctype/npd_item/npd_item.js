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
                    let doc_data = JSON.parse(JSON.stringify(frm.doc));
                    
                    // Exclude metadata and internal keys
                    let exclude_fields = ["name", "is_promoted", "linked_item", "doctype", "owner", "creation", "modified", "modified_by"];
                    exclude_fields.forEach(f => delete doc_data[f]);
                    
                    // Clear item_code and naming_series to let standard Item settings dictate generation
                    delete doc_data.item_code;
                    delete doc_data.naming_series;
                    
                    // Clean up child table auto-generated keys
                    ["barcodes", "uoms", "reorder_levels"].forEach(table_field => {
                        if (doc_data[table_field]) {
                            doc_data[table_field].forEach(row => {
                                delete row.name;
                                delete row.parent;
                                delete row.parentfield;
                                delete row.parenttype;
                            });
                        }
                    });
                    
                    // Establish auto-linking string
                    doc_data.custom_npd_reference = frm.doc.name;
                    
                    // Interactively open standard Item form pre-filled
                    frappe.new_doc("Item", doc_data);
                }).addClass("btn-primary");
            }
        }
    }
});
