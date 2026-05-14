import frappe

def cleanup_client_scripts():
    scripts = frappe.get_all("Client Script", filters=[["name", "like", "NPD%"]], pluck="name")
    for s in scripts:
        frappe.delete_doc("Client Script", s, ignore_permissions=True)
        print(f"Deleted: {s}")
    frappe.db.commit()
    print("Cleanup complete.")
