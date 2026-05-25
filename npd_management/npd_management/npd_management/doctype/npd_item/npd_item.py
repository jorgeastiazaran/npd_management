# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

# Fields that belong only to NPD Item and must NOT be copied to the standard Item
_NPD_ONLY_FIELDS = {
    "name", "is_promoted", "linked_item", "doctype", "owner", "creation",
    "modified", "modified_by", "modified_by_full_name", "idx", "__islocal",
    "naming_series", "item_code",
    # NPD nutritional custom fields (start blank on promotion - user fills them in)
    "npdi_default_nutritional_profile", "npdi_nutrition_per_100g_kcal",
    "npdi_section_nutrition", "npdi_include_in_nutrient_calc",
}

# Child table fields on NPD Item and their corresponding field name on the standard Item
_CHILD_TABLE_FIELDS = [
    "barcodes", "uoms", "reorder_levels", "attributes",
    "item_defaults", "supplier_items", "customer_items", "taxes",
]

# Row-level keys Frappe adds that must be stripped before passing to a new doc
_ROW_META_KEYS = {"name", "parent", "parentfield", "parenttype", "owner",
                  "creation", "modified", "modified_by", "idx", "doctype"}


class NPDItem(Document):
    def before_insert(self):
        # When using naming_series:, Frappe generates the name first.
        # We then copy it to item_code.
        if not self.item_code:
            self.item_code = self.name

    @frappe.whitelist()
    def promote_to_production(self):
        """Promotes the NPD Item to a real Item in ERPNext (legacy backend path)."""
        if self.is_promoted:
            frappe.throw("This item has already been promoted to production.")

        doc_data = self._build_item_data()
        try:
            doc = frappe.get_doc(doc_data)
            doc.insert(ignore_permissions=True)
            self._post_promotion(doc.name)
            frappe.msgprint(f"Successfully created Item {doc.name} in ERPNext.")
            return doc.name
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "NPD Promotion Error")
            frappe.throw(f"Failed to promote to ERPNext: {str(e)}")

    @frappe.whitelist()
    @staticmethod
    def get_promotion_data(npd_item_name):
        """
        Returns a clean dict of all NPD Item fields mapped for a new standard Item.
        Called by the frontend before opening the full Item form, so the user can
        review and adjust values before the document is saved.
        """
        npd = frappe.get_doc("NPD Item", npd_item_name)
        if npd.is_promoted:
            frappe.throw("This NPD Item has already been promoted to production.")
        return npd._build_item_data()

    def _build_item_data(self):
        """Build a clean Item dict from this NPD Item, ready for frappe.get_doc() or route_options."""
        raw = self.as_dict()

        # Get the set of fields that actually exist on the standard Item doctype
        item_meta_fields = {f.fieldname for f in frappe.get_meta("Item").fields}

        item_data = {"doctype": "Item"}

        for key, value in raw.items():
            if key in _NPD_ONLY_FIELDS:
                continue
            if key.startswith("_"):
                continue
            # Only include if the target Item doctype actually has this field
            if key in item_meta_fields:
                item_data[key] = value

        # Copy child tables, stripping row metadata
        for table_field in _CHILD_TABLE_FIELDS:
            rows = raw.get(table_field)
            if rows:
                clean_rows = []
                for row in rows:
                    clean_row = {k: v for k, v in row.items() if k not in _ROW_META_KEYS}
                    clean_rows.append(clean_row)
                item_data[table_field] = clean_rows

        # Mark that this Item was promoted from the NPD record
        item_data["custom_npd_reference"] = self.name

        return item_data

    def _post_promotion(self, item_name):
        """Mark the NPD Item as promoted and link it to the created Item."""
        self.is_promoted = 1
        self.linked_item = item_name
        if not self.item_code:
            self.item_code = item_name
        self.save(ignore_permissions=True)

        # Copy Nutritional Profiles
        profiles = frappe.get_all("Nutritional Profile", filters={
            "reference_doctype": "NPD Item",
            "reference_name": self.name
        })
        for profile_info in profiles:
            profile_doc = frappe.get_doc("Nutritional Profile", profile_info.name)
            new_profile = frappe.copy_doc(profile_doc)
            new_profile.reference_doctype = "Item"
            new_profile.reference_name = item_name
            new_profile.insert(ignore_permissions=True)


# Expose the static method at the module level for frappe.call route
get_promotion_data = NPDItem.get_promotion_data
