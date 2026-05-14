import frappe

CLIENT_SCRIPTS = [
    # ─── NPD Item ────────────────────────────────────────────────────────────
    {
        "name": "NPD Item - Naming",
        "dt": "NPD Item",
        "view": "Form",
        "enabled": 1,
        "script": """
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
        }
    }
});
""",
    },

    # ─── NPD BOM ─────────────────────────────────────────────────────────────
    {
        "name": "NPD BOM - Item Type Sync",
        "dt": "NPD BOM",
        "view": "Form",
        "enabled": 1,
        "script": """
frappe.ui.form.on("NPD BOM", {
    item_doctype: function(frm) {
        // Clear main item when parent type changes
        frm.set_value("item", "");
    },
    default_item_doctype: function(frm) {
        // Bulk update child rows to match the table's Default Item Type
        if (frm.doc.items && frm.doc.items.length > 0) {
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
    }
});

frappe.ui.form.on("NPD BOM Item", {
    items_add: function(frm, cdt, cdn) {
        // New row inherits default Item Type for table
        if (frm.doc.default_item_doctype) {
            frappe.model.set_value(cdt, cdn, "item_doctype", frm.doc.default_item_doctype);
        }
    },
    item_doctype: function(frm, cdt, cdn) {
        // Clear item when type changes in a row
        frappe.model.set_value(cdt, cdn, "item_code", "");
    },
    item_code: function(frm, cdt, cdn) {
        // Exactly mirrors ERPNext BOM.js get_bom_material_detail pattern:
        // frappe.call({ doc: doc, method: "...", ... }) passes the full doc to server.
        var d = locals[cdt][cdn];
        if (!d.item_code) return;

        return frappe.call({
            doc: frm.doc,
            method: "get_bom_material_detail",
            args: {
                args: {
                    item_code: d.item_code,
                    item_doctype: d.item_doctype || frm.doc.default_item_doctype || "NPD Item",
                    qty: d.qty || 1,
                    uom: d.uom,
                    stock_uom: d.stock_uom
                }
            },
            callback: function(r) {
                if (r.message) {
                    // Re-fetch row reference (async callback; row may have shifted)
                    d = locals[cdt][cdn];
                    $.extend(d, r.message);
                    refresh_field("items");
                }
            },
            freeze: true
        });
    }
});
""",
    },

    # ─── NPD Supplier Quotation ───────────────────────────────────────────────
    {
        "name": "NPD Supplier Quotation - Promote",
        "dt": "NPD Supplier Quotation",
        "view": "Form",
        "enabled": 1,
        "script": """
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
""",
    },

    # ─── NPD RFQ ─────────────────────────────────────────────────────────────
    {
        "name": "NPD RFQ - Create Quotations",
        "dt": "NPD RFQ",
        "view": "Form",
        "enabled": 1,
        "script": """
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
""",
    },
]


def setup_all():
    """Create or update all NPD client scripts."""
    print("Setting up NPD Client Scripts...")
    for script_def in CLIENT_SCRIPTS:
        name = script_def["name"]
        dt = script_def["dt"]
        view = script_def.get("view", "Form")

        # Delete any old scripts for this dt/view that have a different name
        # (handles renamed scripts or duplicates from prior runs)
        existing = frappe.get_all(
            "Client Script",
            filters={"dt": dt, "view": view},
            pluck="name"
        )
        for old_name in existing:
            if old_name != name:
                frappe.delete_doc("Client Script", old_name, ignore_permissions=True)
                print(f"  ✗ Removed old script: {old_name}")

        if frappe.db.exists("Client Script", name):
            doc = frappe.get_doc("Client Script", name)
        else:
            doc = frappe.new_doc("Client Script")
            doc.name = name

        doc.update(script_def)
        doc.save(ignore_permissions=True)
        print(f"  ✓ {name}")

    frappe.db.commit()
    print("All NPD client scripts set up successfully.")
