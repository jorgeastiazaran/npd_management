frappe.ui.form.on("NPD Nutritional Profile", {
    refresh: function(frm) {
        if (frm.doc.is_locked) {
            frm.disable_save();
            frm.dashboard.set_headline_alert(
                '<div class="alert alert-warning">' +
                '🔒 Este perfil está bloqueado porque está referenciado por una NPD BOM enviada. ' +
                'Para modificar los valores, crea una nueva versión.' +
                '</div>'
            );
        }

        if (!frm.is_new() && !frm.doc.is_locked) {
            frm.add_custom_button(__("Set as Default"), function() {
                frm.set_value("is_default", 1);
                frm.save();
            }, __("Actions")).addClass(frm.doc.is_default ? "btn-default" : "btn-primary");
        }
    },

    npd_item: function(frm) {
        // Auto-generate title when item is selected
        if (frm.doc.npd_item && !frm.doc.title) {
            frm.set_value("title", frm.doc.npd_item + " — Perfil Nutricional");
        }
    },

    item_code: function(frm) {
        if (frm.doc.item_code && !frm.doc.title) {
            frm.set_value("title", frm.doc.item_code + " — Perfil Nutricional");
        }
    }
});
