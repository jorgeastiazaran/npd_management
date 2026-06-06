# NPD Management — NPD Supplier

## Overview
The **NPD Supplier** is an isolated vendor profile used exclusively for Research & Development (R&D) activities. It allows you to record prospective suppliers without affecting your live procurement records. Once the supplier is fully validated and approved, you can promote it to a standard ERPNext **Supplier** with a single click.

---

## Document Fields

| Field               | Description                                                                 |
| ------------------- | --------------------------------------------------------------------------- |
| **Supplier Name**   | The name of the supplier as it will appear in the system.                   |
| **Contact**         | Link to a **Contact** record. When selected, fields below are auto-filled.  |
| **Address**         | Link to an **Address** record. When selected, city, state, country, etc. are pulled. |
| **Mobile No.**      | Dynamically fetched from the selected Contact. Read only.                   |
| **Email Id**        | Dynamically fetched from the selected Contact. Read only.                   |
| **Evaluation Status** | One of: **Draft**, **Pending Review**, **Approved**. See workflow below.    |

### Dynamic Fetching of Contact / Address
- When you link a **Contact**, the system automatically copies the **Mobile No.** and **Email Id** from that contact into this document.
- When you link an **Address**, the address details (City, State, Country, Pincode) are copied into the respective fields.
- These fields are read-only after fetching; any changes must be made in the source **Contact** or **Address** doctype.

---

## Evaluation Status Workflow

The `Evaluation Status` field governs the lifecycle of the NPD Supplier:

1. **Draft** – The record is being created and is editable.
2. **Pending Review** – The supplier details are submitted for review. The document becomes read-only until a decision is made.
3. **Approved** – The supplier has been reviewed and accepted. At this point, a **Promote to Supplier** button appears (see next section).

You can move between **Draft** and **Pending Review** freely. Once **Approved**, the status is final.

---

## Promotion Workflow

When the `Evaluation Status` is **Approved**, a section titled **Promotion** appears at the bottom of the form with a **Promote to Supplier** button.

### What happens when you click “Promote to Supplier”?
1. A new standard **Supplier** doctype is created in ERPNext.
2. The following data is migrated from the NPD Supplier:
   - Supplier Name
   - Contact (linked)
   - Address (linked)
   - Mobile No.
   - Email Id
3. The NPD Supplier record is now **Read Only** – no further editing is allowed.
4. A **Supplier** field on the NPD Supplier form shows the link to the newly created live Supplier.

> [!WARNING]
> Promotion is irreversible. Only NPD Suppliers with **Approved** status can be promoted.

---

## After Promotion

- The NPD Supplier document remains visible for reference but cannot be edited.
- The associated **Contact** and **Address** records are now shared with the live Supplier.
- The promoted standard Supplier can be used in all normal ERPNext Purchase transactions.

---

## Example Use Case

1. R&D creates an NPD Supplier “Acme Innovations”.
2. They link a Contact (John Doe, +1-555-0123) and an Address (123 R&D Lane).
3. The supplier passes internal validation; status changed to **Approved**.
4. The R&D manager clicks **Promote to Supplier**.
5. A standard Supplier “Acme Innovations” is created with the same contact details.
6. The NPD Supplier becomes read-only, and a link to the live Supplier is recorded.
