frappe.ui.form.on('NPD Trial', {
	setup: function(frm) {
		// Filter BOM No based on selected Production Item
		frm.set_query("bom_no", function() {
			if (frm.doc.production_item) {
				return {
					filters: {
						item: frm.doc.production_item
					}
				};
			}
		});
	},
	
	production_item: function(frm) {
		// Clear BOM if production item changes
		frm.set_value('bom_no', null);
		frm.clear_table('required_items');
		frm.set_value('total_material_cost', 0);
		frm.refresh_field('required_items');
	},
	
	bom_no: function(frm) {
		fetch_and_set_bom_items(frm);
	},
	
	qty: function(frm) {
		if (frm.doc.bom_no) {
			fetch_and_set_bom_items(frm);
		}
	}
});

frappe.ui.form.on('NPD Trial Item', {
	required_qty: function(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, 'amount', flt(row.required_qty) * flt(row.rate));
		calculate_total_material_cost(frm);
	},
	rate: function(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, 'amount', flt(row.required_qty) * flt(row.rate));
		calculate_total_material_cost(frm);
	}
});

function calculate_total_material_cost(frm) {
	let total = 0;
	if (frm.doc.required_items) {
		frm.doc.required_items.forEach(row => {
			total += flt(row.amount);
		});
	}
	frm.set_value('total_material_cost', total);
}

function fetch_and_set_bom_items(frm) {
	if (!frm.doc.bom_no || !frm.doc.qty) {
		return;
	}
	
	frappe.model.with_doc("NPD BOM", frm.doc.bom_no, function() {
		let bom = frappe.model.get_doc("NPD BOM", frm.doc.bom_no);
		frm.clear_table("required_items");
		
		let bom_qty = flt(bom.quantity) || 1.0;
		
		if (bom && bom.items) {
			bom.items.forEach(function(row) {
				let child = frm.add_child("required_items");
				child.item_doctype = row.item_doctype || 'NPD Item';
				child.item_code = row.item_code;
				child.item_name = row.item_name;
				child.description = row.description;
				child.uom = row.uom;
				child.stock_uom = row.stock_uom;
				child.rate = row.rate;
				
				// Standard Work Order formula: (BOM Item Qty / BOM Base Qty) * Trial Qty
				let item_qty = flt(row.qty);
				child.required_qty = (item_qty / bom_qty) * flt(frm.doc.qty);
				child.amount = flt(child.required_qty) * flt(child.rate);
			});
			frm.refresh_field("required_items");
			calculate_total_material_cost(frm);
		}
	});
}

frappe.ui.form.on('NPD Trial Note', {
	note: function(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if (!row.added_by) {
			frappe.model.set_value(cdt, cdn, 'added_by', frappe.session.user);
			frappe.model.set_value(cdt, cdn, 'added_on', frappe.datetime.now_datetime());
		}
	}
});

