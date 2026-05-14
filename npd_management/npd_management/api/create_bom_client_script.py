import frappe

def create_bom_client_script():
    script_name = "NPD BOM - Item Type Sync"

    if frappe.db.exists("Client Script", script_name):
        doc = frappe.get_doc("Client Script", script_name)
        print(f"Updating existing Client Script: {script_name}")
    else:
        doc = frappe.new_doc("Client Script")
        doc.name = script_name
        print(f"Creating new Client Script: {script_name}")

    doc.dt = "NPD BOM"
    doc.view = "Form"
    doc.enabled = 1
    doc.script = """
frappe.ui.form.on("NPD BOM", {
    setup: function(frm) {
        // Filter for main item dynamic link based on item_doctype
        frm.set_query("item", function() {
            return {};
        });
    },
    item_doctype: function(frm) {
        // Clear main item when type changes
        frm.set_value("item", "");

        // Bulk update child rows to match the global Item Type
        if (frm.doc.items && frm.doc.items.length > 0) {
            frappe.confirm(
                __("Update Item Type for all rows in the Items table to '{0}'?", [frm.doc.item_doctype]),
                () => {
                    frm.doc.items.forEach(function(row) {
                        frappe.model.set_value(row.doctype, row.name, "item_doctype", frm.doc.item_doctype);
                        frappe.model.set_value(row.doctype, row.name, "item_code", "");
                    });
                    frm.refresh_field("items");
                    frappe.show_alert({message: __("Updated all rows to: {0}", [frm.doc.item_doctype]), indicator: "green"});
                }
            );
        }
    }
});

frappe.ui.form.on("NPD BOM Item", {
    items_add: function(frm, cdt, cdn) {
        // Inherit global Item Type when adding a new row
        if (frm.doc.item_doctype) {
            frappe.model.set_value(cdt, cdn, "item_doctype", frm.doc.item_doctype);
        }
    },
    item_doctype: function(frm, cdt, cdn) {
        // Clear item_code when type changes in a specific row
        frappe.model.set_value(cdt, cdn, "item_code", "");
    }
});
"""
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"Client Script '{script_name}' saved successfully.")

if __name__ == "__main__":
    create_bom_client_script()
