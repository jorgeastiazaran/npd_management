// Copyright (c) 2026, Tecnofood and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPD BOM Comparison', {
    refresh: function(frm) {
        frm.add_custom_button(__('Generate Comparison'), function() {
            frm.trigger('compare_boms');
        }).addClass('btn-primary');
    },
    
    base_bom: function(frm) {
        if (frm.doc.base_bom && frm.doc.compare_bom) {
            frm.trigger('compare_boms');
        }
    },
    
    compare_bom: function(frm) {
        if (frm.doc.base_bom && frm.doc.compare_bom) {
            frm.trigger('compare_boms');
        }
    },
    
    compare_boms: function(frm) {
        if (!frm.doc.base_bom || !frm.doc.compare_bom) {
            frappe.msgprint(__('Please select both Base BOM and Compare BOM targets to execute structural auditing.'));
            return;
        }
        
        frappe.call({
            method: 'npd_management.npd_management.doctype.npd_bom_comparison.npd_bom_comparison.get_bom_comparison_json',
            args: {
                base_bom: frm.doc.base_bom,
                compare_bom: frm.doc.compare_bom
            },
            freeze: true,
            freeze_message: __('Arraying formulation structures and calculating deltas...'),
            callback: function(r) {
                if (!r.exc && r.message) {
                    render_comparison_grid(frm, r.message);
                }
            }
        });
    }
});

function render_comparison_grid(frm, data) {
    frm.set_value('cost_variance', flt(data.total_variance));
    
    let html = `<div class="bom-delta-container" style="margin-top: 15px; border: 1px solid #d1d8dd; border-radius: 6px; background: #fff;">
        <div style="padding: 12px 15px; background: #f8f9fa; border-bottom: 1px solid #d1d8dd; font-weight: bold;">
            ${__('Formulation Variance Breakdown')}
        </div>
        <div style="padding: 15px;">
            <table class="table table-bordered" style="margin-bottom: 0;">
                <thead>
                    <tr style="background: #f4f5f6;">
                        <th style="width: 15%;">${__('Status')}</th>
                        <th style="width: 25%;">${__('Item Code')}</th>
                        <th style="width: 30%;">${__('Item Name')}</th>
                        <th style="width: 15%; text-align: right;">${__('Qty Delta')}</th>
                        <th style="width: 15%; text-align: right;">${__('Cost Impact')}</th>
                    </tr>
                </thead>
                <tbody>`;
                
    if (data.added && data.added.length) {
        data.added.forEach(row => {
            html += `<tr style="background: #eefaf0;">
                <td><span class="indicator green" style="font-weight:600;">${__('Added')}</span></td>
                <td><b>${row.item_code}</b></td>
                <td>${row.item_name}</td>
                <td style="text-align: right; color: #28a745;">+${flt(row.qty, 4)} ${row.uom}</td>
                <td style="text-align: right; color: #28a745;">+${format_currency(row.cost_variance)}</td>
            </tr>`;
        });
    }
    
    if (data.removed && data.removed.length) {
        data.removed.forEach(row => {
            html += `<tr style="background: #fdf2f2;">
                <td><span class="indicator red" style="font-weight:600;">${__('Removed')}</span></td>
                <td><del>${row.item_code}</del></td>
                <td><del>${row.item_name}</del></td>
                <td style="text-align: right; color: #dc3545;">-${flt(row.qty, 4)} ${row.uom}</td>
                <td style="text-align: right; color: #dc3545;">${format_currency(row.cost_variance)}</td>
            </tr>`;
        });
    }
    
    if (data.changed && data.changed.length) {
        data.changed.forEach(row => {
            let qty_str = row.qty_diff > 0 ? `+${flt(row.qty_diff, 4)}` : `${flt(row.qty_diff, 4)}`;
            let cost_color = row.cost_variance > 0 ? '#28a745' : row.cost_variance < 0 ? '#dc3545' : '#495057';
            let cost_sign = row.cost_variance > 0 ? '+' : '';
            
            html += `<tr style="background: #fffdf2;">
                <td><span class="indicator orange" style="font-weight:600;">${__('Modified')}</span></td>
                <td><b>${row.item_code}</b></td>
                <td>${row.item_name}<br><small class="text-muted">${__('Base')}: ${flt(row.base_qty, 4)} vs ${__('Baseline')}: ${flt(row.comp_qty, 4)}</small></td>
                <td style="text-align: right;">${qty_str} ${row.uom}</td>
                <td style="text-align: right; color: ${cost_color};">${cost_sign}${format_currency(row.cost_variance)}</td>
            </tr>`;
        });
    }
    
    if (data.unchanged && data.unchanged.length) {
        data.unchanged.forEach(row => {
            html += `<tr>
                <td><span class="indicator grey">${__('Identical')}</span></td>
                <td>${row.item_code}</td>
                <td class="text-muted">${row.item_name}</td>
                <td style="text-align: right; color: #adb5bd;">${flt(row.qty, 4)} ${row.uom}</td>
                <td style="text-align: right; color: #adb5bd;">${format_currency(0)}</td>
            </tr>`;
        });
    }
    
    if (!data.added.length && !data.removed.length && !data.changed.length && !data.unchanged.length) {
        html += `<tr><td colspan="5" class="text-center text-muted" style="padding: 20px;">${__('No material line items documented in candidate array.')}</td></tr>`;
    }
    
    html += `</tbody></table></div>
        <div style="padding: 10px 15px; background: #f8f9fa; border-top: 1px solid #d1d8dd; text-align: right;">
            <b>${__('Base Formulation Variance')}:</b> 
            <span style="font-size: 1.1em; color: ${data.total_variance > 0 ? '#28a745' : data.total_variance < 0 ? '#dc3545' : '#333'}; font-weight: bold;">
                ${data.total_variance > 0 ? '+' : ''}${format_currency(data.total_variance)}
            </span>
        </div>
    </div>`;
    
    frm.set_value('comparison_html', html);
    // Suppress secondary triggering during rendering cycle
    frm.save();
}
