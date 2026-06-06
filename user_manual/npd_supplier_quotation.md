# NPD Management — NPD Supplier Quotation

## Overview
The **NPD Supplier Quotation** is a provisional pricing and specification document collected from an **NPD Supplier** for **NPD Items**. It mirrors a standard Supplier Quotation but stays isolated from live procurement until both the supplier and the items have been promoted.

---

## Document Fields & Sections

### Header

| Field            | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| **NPD Supplier** | Link to an approved NPD Supplier. Only **Approved** NPD Suppliers are selectable. |
| **Currency**     | The currency in which the quotation is priced (e.g., USD, EUR, INR).        |
| **Price List**   | The applicable price list (e.g., Standard Buying). Used for rate calculation. |
| **Status**       | Defaults to **Draft**. Becomes **Submitted** when the user clicks **Submit**. |

### Items Table

Each row in the Items table includes:

| Field            | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| **NPD Item**     | Link to an **NPD Item** (from the NPD Item doctype).         |
| **Item Name**    | Auto-fetched from the NPD Item.                               |
| **Qty**          | Quantity quoted.                                              |
| **Rate**         | Provisional unit price in the selected currency.              |
| **Amount**       | Computed as Qty × Rate.                                       |
| **Delivery Date**| Estimated delivery date (optional).                           |

Only NPD Items that have **not yet been promoted** to standard Items can be added. Once an NPD Item inside the quotation is promoted, it becomes read-only in this table.

### Taxes Section

You can add tax rows (e.g., VAT, GST, Shipping) just like in a standard Supplier Quotation:

| Field      | Description                                      |
| ---------- | ------------------------------------------------ |
| **Charge Type** | Actual, Inclusive, etc.                   |
| **Account Head** | The tax Account (e.g., Output Tax CGST).  |
| **Rate**   | Tax percentage or fixed amount.                  |
| **Amount** | Computed automatically.                          |

---

## Workflow & Status

| Action                 | Effect                                                                 |
| ---------------------- | ---------------------------------------------------------------------- |
| **Save** (Draft)       | Quotation is saved and editable.                                       |
| **Submit**             | Changes the Status from **Draft** to **Submitted**. Document becomes read-only. |
| **Cancel**             | Only possible after submission. Resets status to **Cancelled**.        |

---

## Promotion Workflow

Promotion of an NPD Supplier Quotation to a standard **Supplier Quotation** is a two-step prerequisite:

1. **The NPD Supplier** (linked in the header) must have been promoted to a live Supplier.
2. **All NPD Items** listed in the quotation must have been promoted to standard Items.

When both conditions are met, a **Promote to Supplier Quotation** button appears in a **Promotion** section.

### What happens when you click “Promote to Supplier Quotation”?
1. A new standard **Supplier Quotation** doctype is created.
2. The following data is copied:
   - Supplier (now the live Supplier)
   - Currency, Price List
   - Items (now live Items) with same Qty, Rate, Amount
   - Taxes section
3. The NPD Supplier Quotation becomes **Read Only**.
4. A link to the created standard Supplier Quotation is stored in a field on the NPD Supplier Quotation form.

> [!NOTE]
> If any NPD Item is not yet promoted, the button remains hidden or disabled.

---

## After Promotion

- The NPD Supplier Quotation document is frozen for reference.
- The newly created standard Supplier Quotation can be used in live Purchase Orders and RFQs.
- All items now point to live ERPNext Items; the provisional data is preserved in the NPD version.

---

## Example Use Case

1. R&D creates an NPD Supplier Quotation for “Acme Innovations” (which is still an NPD Supplier).
2. They add three NPD Items: “Prototype PCB”, “Custom Sensor”, “Bracket”.
3. The quotation is **Submitted** (Status = Submitted).
4. Later, the NPD Supplier “Acme Innovations” is approved and promoted to a live Supplier.
5. One by one, the NPD Items are promoted to standard Items.
6. Once all conditions are met, the **Promote to Supplier Quotation** button appears.
7. Clicking it creates a standard Supplier Quotation with live data.
8. The NPD Supplier Quotation becomes read-only and shows a link to the new live transaction.
