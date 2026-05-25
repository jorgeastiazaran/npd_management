import frappe

def execute():
    logs = frappe.db.get_list('Error Log', fields=['method', 'error', 'creation'], order_by='creation desc', limit=5)
    for l in logs:
        print(f"[{l.creation}] {l.method}")
        print(l.error[:500])
        print("-" * 50)
