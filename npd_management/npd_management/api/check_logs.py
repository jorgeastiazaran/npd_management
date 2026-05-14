import frappe

def check_logs():
    # Subject: Error Log column name is usually 'error' for the long text
    logs = frappe.get_all("Error Log", filters={"subject": ["like", "%NPD%"]}, fields=["error", "subject", "creation"], order_by="creation desc", limit=10)
    if not logs:
        print("No NPD logs found.")
        return
    for log in logs:
        print(f"[{log.creation}] Subject: {log.subject}")
        print(f"Error: {log.error[:500]}...") # Print first 500 chars
        print("-" * 20)
