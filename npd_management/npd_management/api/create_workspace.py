import frappe

def create_npd_workspace():
    workspace_name = "NPD Management"
    
    if frappe.db.exists("Workspace", workspace_name):
        frappe.delete_doc("Workspace", workspace_name)
        
    # Delete any customized workspaces for this page
    frappe.db.sql("delete from `tabWorkspace` where extends=%s", workspace_name)
    
    links = []
    
    # NPD Testing Section
    links.append({"type": "Card Break", "label": "NPD Testing"})
    links.append({"type": "Link", "label": "NPD Item", "link_type": "DocType", "link_to": "NPD Item"})
    links.append({"type": "Link", "label": "NPD BOM", "link_type": "DocType", "link_to": "NPD BOM"})
    links.append({"type": "Link", "label": "NPD Trial", "link_type": "DocType", "link_to": "NPD Trial"})
    links.append({"type": "Link", "label": "Quality Inspection", "link_type": "DocType", "link_to": "NPD Quality Inspection"})
    links.append({"type": "Link", "label": "QI Template", "link_type": "DocType", "link_to": "NPD Quality Inspection Template"})
    
    # NPD Suppliers Section
    links.append({"type": "Card Break", "label": "NPD Suppliers"})
    links.append({"type": "Link", "label": "NPD Supplier", "link_type": "DocType", "link_to": "NPD Supplier"})
    links.append({"type": "Link", "label": "NPD Supplier Quotation", "link_type": "DocType", "link_to": "NPD Supplier Quotation"})
    links.append({"type": "Link", "label": "NPD RFQ", "link_type": "DocType", "link_to": "NPD RFQ"})
    
    # NPD Tools Section
    links.append({"type": "Card Break", "label": "NPD Tools"})
    links.append({"type": "Link", "label": "BOM Comparison Tool", "link_type": "Report", "link_to": "BOM Comparison Tool"})
    
    ws = frappe.get_doc({
        "doctype": "Workspace",
        "name": workspace_name,
        "label": workspace_name,
        "title": workspace_name,
        "icon": "beaker",
        "module": "npd_management",
        "is_standard": 0,
        "public": 1,
        "hide_custom": 1,
        "links": links
    })
    
    ws.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Workspace '{workspace_name}' created successfully (is_standard=0, hide_custom=1).")

if __name__ == "__main__":
    create_npd_workspace()
