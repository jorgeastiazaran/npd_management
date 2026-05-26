# NPD Trial & Trial Note

Before starting commercial production, recipes must be verified through physical test batches in the laboratory or on a pilot manufacturing line. The `npd_management` module provides two main entities to document this trial phase: `NPD Trial` (the sandbox counterpart to a Work Order) and `NPD Trial Note`.

---

## 1. NPD Trial (Sandbox Work Order)

An `NPD Trial` schedules, tracks, and manages the execution of an experimental formulation batch. It monitors the consumption of experimental raw materials and records processing times.

### Step-by-Step Instructions:

1. Navigate to **NPD Trial** list view and click **Add NPD Trial**.
2. Select the target **NPD BOM** or raw recipe.
3. Specify the **Qty to Manufacture** (e.g. 50 Kg trial batch).
4. Select the target **Workstation** (e.g. Test Kitchen, Lab Blender 2).
5. Click **Save** and then **Submit** to set the trial status to "In Progress".
6. Once the physical batch is processed, click the **Create Trial Note** button to log results.

---

## 2. NPD Trial Note

The `NPD Trial Note` is the main observation record where engineers, formulators, and quality lab technicians write down notes, parameters, and results of the trial run.

### Creating an NPD Trial Note:

1. Click **Create Trial Note** from an active `NPD Trial` document (this auto-fills references to the trial, BOM, and manufactured items).
2. Fill in the trial observations:
   - **Trial Status:** (Passed, Failed, Needs Adjustment).
   - **Actual Yield:** Enter the weight or quantity of usable product obtained.
   - **Trial Parameters:** Record critical variables (e.g. Temperature = 85°C, Mix speed = 400 RPM).
   - **Sensory Notes:** Log texture, taste, color, odor, and appearance feedback.
3. Save and submit the document.

> [!TIP]
> Use the sensory feedback and actual yield values to adjust your next `NPD BOM` iteration if the trial results suggest adjustments to the formulation.
