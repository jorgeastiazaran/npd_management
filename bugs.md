# Resolved Bugs: `npd_management`

All bugs and defects identified in the `npd_management` codebase have been successfully resolved:

## 1. Stale Test Suite References (`test_nutrition_rollup.py`) — **[RESOLVED]**
* **File:** [test_nutrition_rollup.py](file:///Users/jorgeastiazaran/Library/CloudStorage/GoogleDrive-tecnofoodmx@gmail.com/My%20Drive/PycharmProjects/erpnext_v13_testing_local_instance/npd_management/npd_management/api/test_nutrition_rollup.py)
* **Description:** The test file imported and attempted to manipulate the old doctype `NPD Nutritional Profile` and SQL table `tabNPD Nutritional Profile` throughout. 
* **Fix Applied:** 
  1. Updated all references of `NPD Nutritional Profile` to `Nutritional Profile` and `tabNPD Nutritional Profile` to `tabNutritional Profile`.
  2. Aligned link references to use the correct schema attributes (`reference_doctype` and `reference_name`) rather than old custom columns (`npd_item` / `item_code`).
  3. Switched mock NPD Item creation from `.insert()` to `.db_insert()` with explicit `name` keys and `"npdi_include_in_nutrient_calc": 1` to bypass dynamic link autonaming series conflicts.
  4. Added a fallback in the core rollup engine `get_kg_conversion_factor` to use static UOM constants (e.g. `0.001` for `g` to `Kg`) if no database UOM table entry is configured for an item.

## 2. Hardcoded Site Name in `create_trial_note.py` — **[RESOLVED]**
* **File:** [create_trial_note.py](file:///Users/jorgeastiazaran/Library/CloudStorage/GoogleDrive-tecnofoodmx@gmail.com/My%20Drive/PycharmProjects/erpnext_v13_testing_local_instance/npd_management/npd_management/npd_management/create_trial_note.py#L4)
* **Description:** The setup script initialized Frappe with a hardcoded site: `frappe.init(site="test.localhost", sites_path="sites")`.
* **Fix Applied:** Modified the file to dynamically resolve the active site name by checking if `frappe.local.site` is already initialized, or falling back to reading the bench container's `sites/currentsite.txt` configuration dynamically.
