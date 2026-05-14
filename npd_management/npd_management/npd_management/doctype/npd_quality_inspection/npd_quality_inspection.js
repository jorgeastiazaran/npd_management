// Copyright (c) 2026, Jorge Astiazaran and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPD Quality Inspection', {
	setup: function(frm) {
		frm.set_query("reference_name", function() {
			if (frm.doc.reference_type === "NPD Trial") {
				return { filters: { docstatus: 1 } };
			} else if (frm.doc.reference_type === "NPD Item") {
				return { filters: { disabled: 0 } };
			}
		});

		// When opening from a dashboard, route_options usually contains the parent reference
		if (frappe.route_options && frappe.route_options.reference_name) {
			let ref_name = frappe.route_options.reference_name;
			
			// Try to detect if it's a Trial or Item based on naming prefixes or a db call
			if (ref_name.startsWith('NPD-TRL') || ref_name.startsWith('NPD-TRIAL')) {
				frappe.route_options.reference_type = 'NPD Trial';
			} else if (ref_name.startsWith('NPD-ITEM') || ref_name.startsWith('NPD-SE')) {
				frappe.route_options.reference_type = 'NPD Item';
			} else {
				// Fallback: check db if prefix isn't obvious
				frappe.db.get_value('NPD Trial', ref_name, 'name').then(r => {
					if (r && r.message) {
						frm.set_value('reference_type', 'NPD Trial');
					} else {
						frappe.db.get_value('NPD Item', ref_name, 'name').then(r2 => {
							if (r2 && r2.message) {
								frm.set_value('reference_type', 'NPD Item');
							}
						});
					}
				});
			}
		}
	},
	
	refresh: function(frm) {
		// If creating a new document and we have a reference_name, trigger the fetch
		if (frm.is_new() && frm.doc.reference_name && frm.doc.reference_type && !frm.doc.item_code) {
			frm.trigger('reference_name');
		}
	},

	reference_name: function(frm) {
		if (frm.doc.reference_type === 'NPD Trial' && frm.doc.reference_name) {
			frappe.db.get_value('NPD Trial', frm.doc.reference_name, 'production_item')
			.then(r => {
				if (r && r.message && r.message.production_item) {
					frm.set_value('item_code', r.message.production_item);
				}
			});
		} else if (frm.doc.reference_type === 'NPD Item' && frm.doc.reference_name) {
			// If inspecting an NPD Item directly, the item_code is the reference name
			frm.set_value('item_code', frm.doc.reference_name);
		}
	},
	
	reference_type: function(frm) {
		// Clear item code if type changes to prevent mismatch
		frm.set_value('item_code', '');
		frm.set_value('reference_name', '');
	}
});
