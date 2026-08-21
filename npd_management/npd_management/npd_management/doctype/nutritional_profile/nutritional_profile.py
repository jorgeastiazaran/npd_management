# Copyright (c) 2026, Jorge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class NutritionalProfile(Document):
	def validate(self):
		if self.is_locked:
			frappe.throw("This Nutritional Profile is locked because it is referenced by a submitted BOM.")
		self.set_item_name()
		self.calculate_energy()
		
	def calculate_energy(self):
		if self.contenido_energetico_kcal:
			self.contenido_energetico_kj = flt(self.contenido_energetico_kcal) * 4.184
		
	def set_item_name(self):
		if self.reference_doctype and self.reference_name:
			try:
				if self.reference_doctype == "Item":
					self.item_name = frappe.db.get_value("Item", self.reference_name, "item_name")
				elif self.reference_doctype == "NPD Item":
					# NPD Item usually has item_name field as well, or we fallback to reference_name
					self.item_name = frappe.db.get_value("NPD Item", self.reference_name, "item_name") or self.reference_name
			except Exception:
				pass

	def on_update(self):
		self.sync_with_parent()

	def sync_with_parent(self):
		if not self.reference_doctype or not self.reference_name:
			return
		
		# If is_default, set it on parent and update parent's kcal
		if self.is_default:
			# Uncheck is_default on other profiles for this item
			frappe.db.sql("""
				UPDATE `tabNutritional Profile` 
				SET is_default = 0 
				WHERE reference_doctype = %s AND reference_name = %s AND name != %s
			""", (self.reference_doctype, self.reference_name, self.name))
			
			try:
				frappe.db.set_value(self.reference_doctype, self.reference_name, {
					"npdi_default_nutritional_profile": self.name,
					"npdi_nutrition_per_100g_kcal": self.contenido_energetico_kcal
				})
			except Exception as e:
				frappe.log_error(message=str(e), title="Sync Nutritional Profile Error")

@frappe.whitelist()
def lock_profile(name):
	frappe.db.set_value("Nutritional Profile", name, "is_locked", 1)

NUTRITIONAL_FIELDS = [
	"sodio_mg", "fibra_dietetica_g", "azucares_g", "carbohidratos_g",
	"grasas_saturadas_g", "grasas_g", "proteinas_g",
	"contenido_energetico_kj", "contenido_energetico_kcal",
	"grasas_trans_g", "colesterol_mg", "vit_d_ug", "calcio_mg",
	"hierro_mg", "potasio_mg", "azucares_anadidos_g"
]

def get_active_profile(npd_item=None, item_code=None):
	filters = {"is_default": 1}
	if npd_item:
		filters["reference_doctype"] = "NPD Item"
		filters["reference_name"] = npd_item
	elif item_code:
		filters["reference_doctype"] = "Item"
		filters["reference_name"] = item_code
	else:
		return None

	profile_name = frappe.db.get_value("Nutritional Profile", filters, "name")
	if profile_name:
		return frappe.get_cached_doc("Nutritional Profile", profile_name).as_dict()
	return None
