# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

class NPDTrial(Document):
    def validate(self):
        self.validate_trial_notes()

    def before_update_after_submit(self):
        self.validate_trial_notes()

    def validate_trial_notes(self):
        if self.is_new():
            return
            
        old_notes = frappe.get_all("NPD Trial Note", filters={"parent": self.name}, fields=["name", "note"])
        old_notes_dict = {n.name: n for n in old_notes}
        
        for note in self.get("trial_notes"):
            if note.is_new() or not note.added_by:
                note.added_by = frappe.session.user
                note.added_on = frappe.utils.now()

            if not note.is_new() and note.name in old_notes_dict:
                old_note = old_notes_dict[note.name]
                # Compare stripped versions to ignore minor whitespace changes by the editor
                old_text = (old_note.note or "").strip()
                new_text = (note.note or "").strip()
                if old_text != new_text:
                    frappe.throw("You cannot edit past Trial Notes. Please append a new note instead.")
                    
        if len(self.get("trial_notes")) < len(old_notes):
            frappe.throw("You cannot delete past Trial Notes.")
