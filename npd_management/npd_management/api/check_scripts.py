import frappe

def execute():
    try:
        scripts = frappe.db.get_list('Client Script', filters={'dt': ('in', ['NPD BOM', 'NPD Trial'])}, fields=['name', 'dt'])
        print(scripts)
    except Exception as e:
        print(e)
