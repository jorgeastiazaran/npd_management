import frappe

def execute():
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Nutritional Profile",
        "module": "npd_management",
        "custom": 0,
        "autoname": "field:title",
        "naming_rule": "By fieldname",
        "editable_grid": 1,
        "track_changes": 1,
        "fields": [
            {
                "fieldname": "title",
                "fieldtype": "Data",
                "label": "Profile Title",
                "reqd": 1,
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "reference_doctype",
                "fieldtype": "Select",
                "label": "Reference Document Type",
                "options": "Item\nNPD Item",
                "default": "Item",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "reference_name",
                "fieldtype": "Dynamic Link",
                "label": "Reference Item",
                "options": "reference_doctype",
                "reqd": 1,
                "in_list_view": 1,
                "in_standard_filter": 1
            },
            {
                "fieldname": "item_name",
                "fieldtype": "Data",
                "label": "Item Name",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "col_break_header",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "is_default",
                "fieldtype": "Check",
                "label": "Is Default Profile",
                "default": "0",
                "in_list_view": 1,
                "description": "Only one profile per item can be the default. Setting this will clear it from other profiles of the same item."
            },
            {
                "fieldname": "is_locked",
                "fieldtype": "Check",
                "label": "Locked",
                "read_only": 1,
                "default": "0",
                "description": "Automatically locked when referenced by a submitted NPD BOM. Locked profiles cannot be edited."
            },
            {
                "fieldname": "reference_quantity_g",
                "fieldtype": "Float",
                "label": "Reference Quantity (g)",
                "default": "100",
                "reqd": 1,
                "description": "The weight in grams that all nutrient values below are based on (default: 100g)"
            },
            {
                "fieldname": "include_in_nutrient_calc",
                "fieldtype": "Check",
                "label": "Include in Nutrient Calculation",
                "default": "1",
                "description": "If unchecked, this item will not contribute to nutritional rollup in any NPD BOM"
            },
            {
                "fieldname": "amended_from",
                "fieldtype": "Link",
                "label": "Amended From",
                "options": "Nutritional Profile",
                "no_copy": 1,
                "print_hide": 1,
                "read_only": 1
            },
            {
                "fieldname": "section_nutrients",
                "fieldtype": "Section Break",
                "label": "Nutritional Values (per reference quantity)"
            },
            {
                "fieldname": "energy_col",
                "fieldtype": "Column Break",
                "label": "Energy"
            },
            {
                "fieldname": "contenido_energetico_kcal",
                "fieldtype": "Float",
                "label": "Contenido Energético (kcal)",
                "default": "0"
            },
            {
                "fieldname": "contenido_energetico_kj",
                "fieldtype": "Float",
                "label": "Contenido Energético (kJ)",
                "default": "0"
            },
            {
                "fieldname": "col_break_macros",
                "fieldtype": "Column Break",
                "label": "Macronutrients"
            },
            {
                "fieldname": "grasas_g",
                "fieldtype": "Float",
                "label": "Grasas (g)",
                "default": "0"
            },
            {
                "fieldname": "grasas_saturadas_g",
                "fieldtype": "Float",
                "label": "Grasas Saturadas (g)",
                "default": "0"
            },
            {
                "fieldname": "grasas_trans_g",
                "fieldtype": "Float",
                "label": "Grasas Trans (g)",
                "default": "0"
            },
            {
                "fieldname": "carbohidratos_g",
                "fieldtype": "Float",
                "label": "Carbohidratos (g)",
                "default": "0"
            },
            {
                "fieldname": "azucares_g",
                "fieldtype": "Float",
                "label": "Azúcares (g)",
                "default": "0"
            },
            {
                "fieldname": "azucares_anadidos_g",
                "fieldtype": "Float",
                "label": "Azúcares Añadidos (g)",
                "default": "0"
            },
            {
                "fieldname": "proteinas_g",
                "fieldtype": "Float",
                "label": "Proteínas (g)",
                "default": "0"
            },
            {
                "fieldname": "sodio_mg",
                "fieldtype": "Float",
                "label": "Sodio (mg)",
                "default": "0"
            },
            {
                "fieldname": "fibra_dietetica_g",
                "fieldtype": "Float",
                "label": "Fibra Dietética (g)",
                "default": "0"
            },
            {
                "fieldname": "section_micros",
                "fieldtype": "Section Break",
                "label": "Micronutrients"
            },
            {
                "fieldname": "colesterol_mg",
                "fieldtype": "Float",
                "label": "Colesterol (mg)",
                "default": "0"
            },
            {
                "fieldname": "col_break_micros",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "calcio_mg",
                "fieldtype": "Float",
                "label": "Calcio (mg)",
                "default": "0"
            },
            {
                "fieldname": "hierro_mg",
                "fieldtype": "Float",
                "label": "Hierro (mg)",
                "default": "0"
            },
            {
                "fieldname": "potasio_mg",
                "fieldtype": "Float",
                "label": "Potasio (mg)",
                "default": "0"
            },
            {
                "fieldname": "vit_d_ug",
                "fieldtype": "Float",
                "label": "Vit D (ug)",
                "default": "0"
            }
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "print": 1,
                "email": 1,
                "report": 1,
                "export": 1,
                "share": 1
            },
            {
                "role": "All",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "print": 1,
                "email": 1,
                "report": 1,
                "export": 1,
                "share": 1
            }
        ]
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
