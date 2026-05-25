// Copyright (c) 2026, Jorge and contributors
// For license information, please see license.txt

frappe.ui.form.on('Nutritional Profile', {
	onload: function(frm) {
		if (frm.is_new() && !frm.doc.reference_doctype) {
			if (frappe.route_options && frappe.route_options.reference_doctype) {
				frm.set_value('reference_doctype', frappe.route_options.reference_doctype);
			} else {
				let route = frappe.get_route();
				if (route && route[0] === "Form" && ["Item", "NPD Item"].includes(route[1])) {
					frm.set_value("reference_doctype", route[1]);
					if (route[2]) {
						frm.set_value("reference_name", route[2]);
					}
				}
			}
		}
	},
	contenido_energetico_kcal: function(frm) {
		if (frm.doc.contenido_energetico_kcal) {
			frm.set_value('contenido_energetico_kj', frm.doc.contenido_energetico_kcal * 4.184);
		}
	},
	reference_name: function(frm) {
		if (frm.doc.reference_doctype && frm.doc.reference_name) {
			frappe.db.get_value(frm.doc.reference_doctype, frm.doc.reference_name, 'item_name')
			.then(r => {
				if (r && r.message) {
					frm.set_value('item_name', r.message.item_name);
				}
			});
		}
	}
});
