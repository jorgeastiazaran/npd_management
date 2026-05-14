import frappe

def create_bom_comparison_report():
    report_name = "BOM Comparison Tool"
    if not frappe.db.exists("Report", report_name):
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": report_name,
            "ref_doctype": "NPD BOM",
            "report_type": "Query Report",
            "module": "npd_management",
            "is_standard": "No"
        })
        report.insert()
        frappe.db.commit()
        print(f"Report '{report_name}' created.")

if __name__ == "__main__":
    create_bom_comparison_report()
