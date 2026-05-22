import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

NUTRITIONAL_FIELD_DEFS = [
    {"fieldname": "sodio_mg", "label": "Sodio (mg)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "fibra_dietetica_g", "label": "Fibra Dietética (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "azucares_g", "label": "Azúcares (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "carbohidratos_g", "label": "Carbohidratos (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "grasas_saturadas_g", "label": "Grasas Saturadas (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "grasas_g", "label": "Grasas (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "proteinas_g", "label": "Proteínas (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "contenido_energetico_kj", "label": "Contenido Energético (kJ)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "contenido_energetico_kcal", "label": "Contenido Energético (kcal)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "grasas_trans_g", "label": "Grasas Trans (g)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "colesterol_mg", "label": "Colesterol (mg)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "vit_d_ug", "label": "Vit D (ug)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "calcio_mg", "label": "Calcio (mg)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "hierro_mg", "label": "Hierro (mg)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "potasio_mg", "label": "Potasio (mg)", "fieldtype": "Float", "read_only": 1},
    {"fieldname": "azucares_anadidos_g", "label": "Azúcares Añadidos (g)", "fieldtype": "Float", "read_only": 1},
]


def _bom_nutrition_fields(insert_after):
    """Build custom fields for BOM nutritional output section."""
    fields = [
        {
            "fieldname": "nutrition_facts_section",
            "label": "Nutritional Information",
            "fieldtype": "Section Break",
            "insert_after": insert_after,
            "collapsible": 1,
        },
        {
            "fieldname": "nutritional_snapshot_locked",
            "label": "Nutritional Snapshot Locked",
            "fieldtype": "Check",
            "insert_after": "nutrition_facts_section",
            "read_only": 1,
            "default": "0",
        },
    ]
    prev = "nutritional_snapshot_locked"
    for nut in NUTRITIONAL_FIELD_DEFS:
        entry = dict(nut)
        entry["insert_after"] = prev
        fields.append(entry)
        prev = nut["fieldname"]
    return fields


def ensure_kg_uom():
    """Ensure the Kg UOM exists for nutritional calculations."""
    if not frappe.db.exists("UOM", "Kg"):
        frappe.get_doc({
            "doctype": "UOM",
            "uom_name": "Kg",
            "must_be_whole_number": 0
        }).insert(ignore_permissions=True)


def after_install():
    """Hook executed after app installation to inject custom fields into standard DocTypes."""
    ensure_kg_uom()
    create_custom_fields(get_custom_fields(), ignore_validate=True)


def get_custom_fields():
    bom_nutrition = _bom_nutrition_fields("description")

    return {
        "Item": [
            {
                "fieldname": "custom_npd_reference",
                "label": "NPD Reference",
                "fieldtype": "Link",
                "options": "NPD Item",
                "insert_after": "item_code",
                "read_only": 1,
                "description": "Reference to the original NPD Item this record was promoted from."
            },
            {
                "fieldname": "npdi_section_nutrition",
                "label": "Nutritional Information (NPD)",
                "fieldtype": "Section Break",
                "insert_after": "custom_npd_reference",
                "collapsible": 1,
                "collapsible_depends_on": "eval:doc.npdi_default_nutritional_profile"
            },
            {
                "fieldname": "npdi_default_nutritional_profile",
                "label": "Active Nutritional Profile",
                "fieldtype": "Link",
                "options": "Nutritional Profile",
                "insert_after": "npdi_section_nutrition",
                "no_copy": 1,
                "read_only": 1,
                "description": "The default NPD Nutritional Profile for this item. Set automatically when a profile is marked as default."
            },
            {
                "fieldname": "npdi_include_in_nutrient_calc",
                "label": "Include in Nutrient Calculation",
                "fieldtype": "Check",
                "insert_after": "npdi_default_nutritional_profile",
                "default": "1",
                "description": "If unchecked, this item will not contribute to nutritional rollup in BOM calculations."
            },
            {
                "fieldname": "npdi_nutrition_per_100g_kcal",
                "label": "Energy (kcal / 100g)",
                "fieldtype": "Float",
                "insert_after": "npdi_include_in_nutrient_calc",
                "no_copy": 1,
                "read_only": 1,
                "description": "Summary field: kcal per 100g from the active nutritional profile."
            }
        ],
        "NPD Item": [
            {
                "fieldname": "npdi_section_nutrition",
                "label": "Nutritional Information (NPD)",
                "fieldtype": "Section Break",
                "insert_after": "published_in_website",
                "collapsible": 1,
                "collapsible_depends_on": "eval:doc.npdi_default_nutritional_profile"
            },
            {
                "fieldname": "npdi_default_nutritional_profile",
                "label": "Active Nutritional Profile",
                "fieldtype": "Link",
                "options": "Nutritional Profile",
                "insert_after": "npdi_section_nutrition",
                "no_copy": 1,
                "read_only": 1,
                "description": "The default NPD Nutritional Profile for this item."
            },
            {
                "fieldname": "npdi_include_in_nutrient_calc",
                "label": "Include in Nutrient Calculation",
                "fieldtype": "Check",
                "insert_after": "npdi_default_nutritional_profile",
                "default": "1"
            },
            {
                "fieldname": "npdi_nutrition_per_100g_kcal",
                "label": "Energy (kcal / 100g)",
                "fieldtype": "Float",
                "insert_after": "npdi_include_in_nutrient_calc",
                "no_copy": 1,
                "read_only": 1
            }
        ],
        "BOM": bom_nutrition,
        "BOM Item": [
            {
                "fieldname": "include_in_nutrient_calc",
                "label": "Include in Nutrient Calculation",
                "fieldtype": "Check",
                "insert_after": "qty",
                "default": "1",
                "in_list_view": 1,
            }
        ],
    }
