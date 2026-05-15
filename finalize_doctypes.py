import os
import json

MAPPINGS = {
    "Item": "NPD Item",
    "BOM": "NPD BOM",
    "BOM Item": "NPD BOM Item",
    "BOM Scrap Item": "NPD BOM Scrap Item",
    "BOM Operation": "NPD BOM Operation",
    "Work Order": "NPD Trial",
    "Work Order Item": "NPD Trial Item",
    "Work Order Operation": "NPD Trial Operation",
    "Quality Inspection Template": "NPD Quality Inspection Template",
    "Quality Inspection": "NPD Quality Inspection",
    "Quality Inspection Reading": "NPD Quality Inspection Reading"
}

NUTRITIONAL_FIELDS = [
    {"fieldname": "nutrition_facts_section", "label": "Nutritional Information", "fieldtype": "Section Break"},
    {"fieldname": "sodio_mg", "label": "Sodio (mg)", "fieldtype": "Float"},
    {"fieldname": "fibra_dietetica_g", "label": "Fibra Dietética (g)", "fieldtype": "Float"},
    {"fieldname": "azucares_g", "label": "Azúcares (g)", "fieldtype": "Float"},
    {"fieldname": "carbohidratos_g", "label": "Carbohidratos (g)", "fieldtype": "Float"},
    {"fieldname": "grasas_saturadas_g", "label": "Grasas Saturadas (g)", "fieldtype": "Float"},
    {"fieldname": "grasas_g", "label": "Grasas (g)", "fieldtype": "Float"},
    {"fieldname": "proteinas_g", "label": "Proteínas (g)", "fieldtype": "Float"},
    {"fieldname": "contenido_energetico_kj", "label": "Contenido Energético (kJ)", "fieldtype": "Float"},
    {"fieldname": "contenido_energetico_kcal", "label": "Contenido Energético (kcal)", "fieldtype": "Float"},
    {"fieldname": "grasas_trans_g", "label": "Grasas Trans (g)", "fieldtype": "Float"},
    {"fieldname": "colesterol_mg", "label": "Colesterol (mg)", "fieldtype": "Float"},
    {"fieldname": "vit_d_ug", "label": "Vit D (ug)", "fieldtype": "Float"},
    {"fieldname": "calcio_mg", "label": "Calcio (mg)", "fieldtype": "Float"},
    {"fieldname": "hierro_mg", "label": "Hierro (mg)", "fieldtype": "Float"},
    {"fieldname": "potasio_mg", "label": "Potasio (mg)", "fieldtype": "Float"},
    {"fieldname": "azucares_anadidos_g", "label": "Azúcares Añadidos (g)", "fieldtype": "Float"}
]

def finalize_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        
    # Update field options if they link to a mapped doctype
    for field in data.get("fields", []):
        if field.get("fieldtype") in ["Link", "Table"]:
            options = field.get("options")
            if options in MAPPINGS:
                field["options"] = MAPPINGS[options]
                
    # Add Nutritional Info to NPD Item and NPD BOM
    if data["name"] in ["NPD Item", "NPD BOM"]:
        # Find a good place to insert (usually at the end or before standard sections)
        data["fields"].extend(NUTRITIONAL_FIELDS)
        
    # Add Costing fields to NPD BOM
    if data["name"] == "NPD BOM":
        costing_fields = [
            {"fieldname": "npd_costing_section", "label": "NPD Costing", "fieldtype": "Section Break"},
            {"fieldname": "valuation_method", "label": "Valuation Method", "fieldtype": "Select", 
             "options": "\nValuation Rate\nLast Purchase Rate", "default": "Valuation Rate"},
            {"fieldname": "total_cost", "label": "Total Cost", "fieldtype": "Float", "read_only": 1}
        ]
        data["fields"].extend(costing_fields)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def main():
    base_path = "npd_management/npd_management/npd_management/doctype"
    for subdir in os.listdir(base_path):
        dir_path = os.path.join(base_path, subdir)
        if os.path.isdir(dir_path):
            json_file = os.path.join(dir_path, f"{subdir}.json")
            if os.path.exists(json_file):
                print(f"Finalizing {json_file}...")
                finalize_json(json_file)

if __name__ == "__main__":
    main()
