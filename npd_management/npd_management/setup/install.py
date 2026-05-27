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
    """
    Hook executed after app installation to inject custom fields into standard DocTypes.
    Idempotent: safe to call multiple times without raising DuplicateEntryError.
    """
    ensure_kg_uom()
    _create_custom_fields_idempotent(get_custom_fields())


def _create_custom_fields_idempotent(custom_fields_map):
    """
    Calls create_custom_fields() only for fields that do not yet exist.
    Makes the installer safe to run on both fresh and partially-migrated sites.
    """
    filtered = {}
    for dt, fields in custom_fields_map.items():
        missing = [
            f for f in fields
            if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": f["fieldname"]})
        ]
        if missing:
            filtered[dt] = missing

    if filtered:
        create_custom_fields(filtered, ignore_validate=True)


# ─── List of ALL custom fields this app injects into standard DocTypes ───────
# Keep this list in sync with get_custom_fields() above.
# Format: (DocType, fieldname)
_NPD_MANAGEMENT_CUSTOM_FIELDS = [
    # Item
    ("Item", "custom_npd_reference"),
    ("Item", "npdi_section_nutrition"),
    ("Item", "npdi_default_nutritional_profile"),
    ("Item", "npdi_include_in_nutrient_calc"),
    ("Item", "npdi_nutrition_per_100g_kcal"),
    # BOM
    ("BOM", "custom_npd_bom_reference"),
    ("BOM", "nutrition_facts_section"),
    ("BOM", "nutritional_snapshot_locked"),
    ("BOM", "contenido_energetico_kcal"),
    ("BOM", "contenido_energetico_kj"),
    ("BOM", "proteinas_g"),
    ("BOM", "grasas_g"),
    ("BOM", "grasas_saturadas_g"),
    ("BOM", "grasas_trans_g"),
    ("BOM", "colesterol_mg"),
    ("BOM", "carbohidratos_g"),
    ("BOM", "azucares_g"),
    ("BOM", "azucares_anadidos_g"),
    ("BOM", "fibra_dietetica_g"),
    ("BOM", "sodio_mg"),
    ("BOM", "potasio_mg"),
    ("BOM", "calcio_mg"),
    ("BOM", "hierro_mg"),
    ("BOM", "vit_d_ug"),
    # BOM Item
    ("BOM Item", "include_in_nutrient_calc"),
    # Supplier
    ("Supplier", "custom_npd_supplier_reference"),
    # Supplier Quotation
    ("Supplier Quotation", "custom_npd_sq_reference"),
    # Quotation
    ("Quotation", "custom_npd_quotation_reference"),
    # Quality Inspection Template
    ("Quality Inspection Template", "custom_npd_qi_template_reference"),
]

# Any physical tables that may be left as orphans (edge-case legacy renames)
_NPD_MANAGEMENT_ORPHAN_TABLES = [
    "tabNPD Nutritional Profile",   # legacy rename artefact
]


def before_uninstall():
    """
    Hook executed before the app is removed from a site.
    Deletes all Custom Fields injected by npd_management so that standard
    DocTypes (BOM, Item, Supplier …) are left completely clean.
    """
    frappe.logger().info("npd_management: running before_uninstall cleanup…")

    # 1. Delete Custom Field records
    for dt, fieldname in _NPD_MANAGEMENT_CUSTOM_FIELDS:
        cf_name = frappe.db.get_value(
            "Custom Field", {"dt": dt, "fieldname": fieldname}
        )
        if cf_name:
            frappe.delete_doc(
                "Custom Field", cf_name,
                ignore_missing=True, ignore_permissions=True, force=True
            )
            frappe.logger().info(f"  Deleted Custom Field: {dt} → {fieldname}")

    # 2. Drop any orphaned physical tables
    for table in _NPD_MANAGEMENT_ORPHAN_TABLES:
        if frappe.db.table_exists(table):
            frappe.db.sql(f"DROP TABLE IF EXISTS `{table}`")
            frappe.logger().info(f"  Dropped orphan table: {table}")

    frappe.db.commit()
    frappe.logger().info("npd_management: before_uninstall cleanup complete.")


def get_custom_fields():
    bom_nutrition = _bom_nutrition_fields("custom_npd_bom_reference")

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
        "BOM": [
            {
                "fieldname": "custom_npd_bom_reference",
                "label": "NPD BOM Reference",
                "fieldtype": "Link",
                "options": "NPD BOM",
                "insert_after": "description",
                "no_copy": 1,
                "read_only": 1,
                "description": "Reference to the NPD BOM this record was promoted from.",
            }
        ] + bom_nutrition,
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
        "Supplier": [
            {
                "fieldname": "custom_npd_supplier_reference",
                "label": "NPD Supplier Reference",
                "fieldtype": "Link",
                "options": "NPD Supplier",
                "insert_after": "supplier_name",
                "no_copy": 1,
                "read_only": 1,
                "description": "Reference to the NPD Supplier this record was promoted from.",
            }
        ],
        "Supplier Quotation": [
            {
                "fieldname": "custom_npd_sq_reference",
                "label": "NPD Supplier Quotation Reference",
                "fieldtype": "Link",
                "options": "NPD Supplier Quotation",
                "insert_after": "supplier",
                "no_copy": 1,
                "read_only": 1,
                "description": "Reference to the NPD Supplier Quotation this record was promoted from.",
            }
        ],
        "Quotation": [
            {
                "fieldname": "custom_npd_quotation_reference",
                "label": "NPD Quotation Reference",
                "fieldtype": "Link",
                "options": "NPD Quotation",
                "insert_after": "party_name",
                "no_copy": 1,
                "read_only": 1,
                "description": "Reference to the NPD Quotation this record was promoted from.",
            }
        ],
        "Quality Inspection Template": [
            {
                "fieldname": "custom_npd_qi_template_reference",
                "label": "NPD Quality Inspection Template Reference",
                "fieldtype": "Link",
                "options": "NPD Quality Inspection Template",
                "insert_after": "quality_inspection_template_name",
                "no_copy": 1,
                "read_only": 1,
                "description": "Reference to the NPD Quality Inspection Template this record was promoted from.",
            }
        ],
    }
