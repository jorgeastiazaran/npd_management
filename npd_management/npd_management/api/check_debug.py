import frappe

def check_debug_logs():
    logs = frappe.get_all("Error Log", filters={"method": "NPD Debug"}, fields=["error", "creation"], order_by="creation desc", limit=30)
    if not logs:
        print("No logs found.")
        return
    for log in logs:
        if "NPD Calculate Cost Method" in log.error:
            print(f"[{log.creation}] {log.error}")
        elif "Fetched Remote Rate" in log.error:
             print(f"[{log.creation}] {log.error}")
        # print("-" * 20)
