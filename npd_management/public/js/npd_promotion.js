/**
 * npd_promotion.js — Shared frontend helper for NPD → Production promotion flows.
 *
 * Usage in any NPD doctype JS:
 *   npd_mgmt.open_promote_form(frm, {
 *       target_doctype: "Item",
 *       api_method: "npd_management.npd_management.doctype.npd_item.npd_item.get_promotion_data",
 *       confirm_msg: "Promote this NPD Item to a live ERPNext Item?",
 *       target_route_key: "item",   // used to build "new-item-1"
 *   });
 */

frappe.provide("npd_mgmt");

/**
 * Open the full production doctype form pre-filled from NPD data.
 *
 * @param {Object} frm           - The current Frappe form object.
 * @param {Object} opts
 * @param {string} opts.target_doctype  - e.g. "BOM", "Supplier", "Quotation"
 * @param {string} opts.api_method      - Whitelisted Python method returning the mapped dict.
 * @param {string} [opts.confirm_msg]   - Custom confirmation message.
 * @param {Function} [opts.pre_validate] - Optional fn(frm) called before routing; can return false to abort.
 */
npd_mgmt.open_promote_form = function(frm, opts) {
    // Build a human-readable "new-foo-bar-1" route key from the doctype name
    let route_key = opts.target_doctype.toLowerCase().replace(/ /g, "-");
    let new_doc_route = `new-${route_key}-1`;

    let msg = opts.confirm_msg ||
        __("This will open a new <b>{0}</b> form pre-filled with data from <b>{1}</b>. Review and save to complete the promotion.", [opts.target_doctype, frm.doc.name]);

    frappe.confirm(msg, function() {
        if (opts.pre_validate && opts.pre_validate(frm) === false) return;

        frappe.show_progress(__("Preparing {0}...", [opts.target_doctype]), 30, 100);

        frappe.call({
            method: opts.api_method,
            args: { npd_item_name: frm.doc.name },   // generic arg name; Python methods use **kwargs pattern
            callback: function(r) {
                frappe.hide_progress();
                if (r.exc || !r.message) return;

                frappe.new_doc(opts.target_doctype, r.message);
            },
            error: function() {
                frappe.hide_progress();
            }
        });
    });
};
