import frappe
import json

def run():
    res = frappe.get_attr('erpnext_npdi_suite.api.get_project_gantt_data')(project='PROJ-0041')
    print("GANTT_DATA_RESULT:")
    for t in res.get("tasks", []):
        if "TASK-2026-02318" in t.values() or "TASK-2026-02319" in t.values() or t.get("parentTaskId") == "TASK-2026-02318":
            print(json.dumps(t, default=str))
