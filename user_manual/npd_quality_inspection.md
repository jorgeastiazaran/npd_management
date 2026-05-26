# NPD Quality Inspection

To guarantee consistency, R&D trials must undergo chemical, physical, and sensory quality checks. The `npd_management` module provides experimental quality tools that allow you to set test profiles and log actual measurements.

---

## 1. NPD Quality Inspection Template

An `NPD Quality Inspection Template` defines the standard test parameters, target ranges, and acceptance criteria for an item group or a specific experimental formulation.

### Setting up a Template:

1. Navigate to **NPD Quality Inspection Template** and click **Add Template**.
2. Give it a descriptive name (e.g. `Lab Test Profile - Sauces`).
3. Under the **Inspection Readings** table, add rows for each test:
   - **Parameter:** (e.g. pH, Viscosity, Brix, Color).
   - **Type:** (Numeric or Value Based).
   - **Minimum & Maximum Value:** (e.g., pH target 3.8 - 4.2).
4. Save the template.

---

## 2. NPD Quality Inspection

When running a trial batch (`NPD Trial`), log the actual laboratory measurements using `NPD Quality Inspection`.

### Creating a Quality Inspection:

1. Open the target **NPD Trial** or **NPD Item** form.
2. Click **Create Quality Inspection** (or navigate to `NPD Quality Inspection` list and click add).
3. Select the target **NPD Quality Inspection Template**. This pulls the predefined parameters and ranges.
4. Input the actual lab values in the **Readings** table:
   - Enter measured values (e.g., pH = 3.9).
   - The system automatically compares the reading against the template's min/max ranges and marks the row as **Passed** or **Failed**.
5. Save the document.

> [!NOTE]
> Recording actual inspections in the sandbox helps developers review product quality history over multiple trials, providing an audit trail for final product sign-off.
