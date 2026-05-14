import frappe

def debug_npd_bom_controller():
    meta = frappe.get_meta("NPD BOM")
    print(f"module: {meta.module}")
    print(f"custom: {meta.custom}")
    
    doc = frappe.get_doc({"doctype": "NPD BOM"})
    print(f"controller class: {doc.__class__.__name__}")
    print(f"controller module: {doc.__class__.__module__}")
    print(f"has get_bom_material_detail: {hasattr(doc, 'get_bom_material_detail')}")
    
    # Check where Frappe is looking for the controller
    from frappe.modules import get_module_path
    module_path = get_module_path(meta.module)
    print(f"module_path: {module_path}")
