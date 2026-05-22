# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt


NUTRITIONAL_FIELDS = [
    "sodio_mg", "fibra_dietetica_g", "azucares_g", "carbohidratos_g",
    "grasas_saturadas_g", "grasas_g", "proteinas_g", "contenido_energetico_kj",
    "contenido_energetico_kcal", "grasas_trans_g", "colesterol_mg",
    "vit_d_ug", "calcio_mg", "hierro_mg", "potasio_mg", "azucares_anadidos_g"
]


class NPDNutritionalProfile(Document):

    def validate(self):
        if not self.npd_item and not self.item_code:
            frappe.throw("Please link this profile to an NPD Item or an ERPNext Item.")
        if self.is_locked:
            frappe.throw(
                "Este perfil nutricional está bloqueado porque está referenciado por una "
                "NPD BOM enviada. Para modificarlo, crea una nueva versión."
            )
        if self.is_default:
            self._ensure_single_default()
        if not self.title:
            item_label = self.npd_item or self.item_code or "Item"
            self.title = f"{item_label} — Perfil Nutricional"

    def _ensure_single_default(self):
        """Unset is_default on all other profiles for the same item."""
        filters = {"is_default": 1, "name": ["!=", self.name or "__new__"]}
        if self.npd_item:
            filters["npd_item"] = self.npd_item
        elif self.item_code:
            filters["item_code"] = self.item_code

        existing = frappe.get_all("NPD Nutritional Profile", filters=filters, fields=["name"])
        for other in existing:
            frappe.db.set_value("NPD Nutritional Profile", other.name, "is_default", 0)

    def on_update(self):
        """When marked as default, sync summary fields back to Item / NPD Item."""
        if self.is_default:
            self._sync_to_item()

    def _sync_to_item(self):
        """Update the summary custom fields on the linked Item or NPD Item."""
        kcal = flt(self.contenido_energetico_kcal)
        if self.item_code and frappe.db.exists("Item", self.item_code):
            frappe.db.set_value("Item", self.item_code, {
                "npdi_default_nutritional_profile": self.name,
                "npdi_nutrition_per_100g_kcal": kcal
            })
        if self.npd_item and frappe.db.exists("NPD Item", self.npd_item):
            frappe.db.set_value("NPD Item", self.npd_item, {
                "npdi_default_nutritional_profile": self.name,
                "npdi_nutrition_per_100g_kcal": kcal,
            })


@frappe.whitelist()
def get_active_profile(npd_item=None, item_code=None):
    """
    Return the active (is_default=1) NPD Nutritional Profile for a given item.
    Prefers npd_item link; falls back to item_code.
    Returns the document as a dict, or None if not found.
    """
    filters = {"is_default": 1}
    if npd_item:
        filters["npd_item"] = npd_item
    elif item_code:
        filters["item_code"] = item_code
    else:
        return None

    result = frappe.get_all(
        "NPD Nutritional Profile",
        filters=filters,
        fields=["name"] + NUTRITIONAL_FIELDS + ["reference_quantity_g", "include_in_nutrient_calc"],
        limit=1
    )
    return result[0] if result else None


@frappe.whitelist()
def lock_profile(profile_name):
    """Lock a nutritional profile so it cannot be edited (called on NPD BOM submit)."""
    frappe.db.set_value("NPD Nutritional Profile", profile_name, "is_locked", 1)
