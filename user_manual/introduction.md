# NPD Management Introduction

Welcome to the **New Product Development (NPD) Management** module for ERPNext. This module is designed to provide an isolated, secure **R&D Sandbox Testing Layer** for food industry laboratories, formulators, and trial engineers.

With this module, you can design and test formulations, log trial batches, request supplier pricing, and perform quality checks without cluttering your core enterprise catalogs or impacting your accounting master ledger.

---

## 🏗️ Core Architecture & The Sandbox Layer

In standard ERPNext, creating items, bills of materials (BOMs), and work orders affects master data, standard costs, and ledger evaluations. The NPD module introduces decoupled, mirrored proxy entities that exist strictly for R&D purposes:

| Production DocType | R&D Sandbox Proxy DocType | Purpose in Sandbox |
| :--- | :--- | :--- |
| **Item** | `NPD Item` | Experimental ingredients, raw materials, or prototypes. |
| **BOM** | `NPD BOM` | Experimental recipe formulations and cost simulation. |
| **Work Order** | `NPD Trial` | Sandbox trial batch execution in the lab or pilot line. |
| **Quality Inspection** | `NPD Quality Inspection` | Custom quality readings for lab trial results. |
| **Supplier** | `NPD Supplier` | Sandbox supplier directory for R&D-only contacts. |
| **RFQ** | `NPD RFQ` | Requesting price/spec quotes for experimental ingredients. |
| **Supplier Quotation** | `NPD Supplier Quotation` | Storing supplier pricing for sandbox formulations. |
| **Quotation** | `NPD Quotation` | Customer quotation simulation for prototype items. |

### Structural Parity Policy

To ensure that your sandbox layouts perfectly mirror your live production forms, the application is deployed with a dynamic installer. This installer copies standard customization parameters (`tabCustom Field` and `tabProperty Setter`) directly into their R&D proxies. This ensures:
1. Form elements match standard layouts (same fields, validation, and options).
2. Upgrades or custom field adjustments in production can be mirrored into the sandbox.
3. Once approved, R&D proxy records can be seamlessly converted ("promoted") into production records with zero data translation loss.

---

## 🔒 Security & Local Execution

Once installed, the NPD application operates entirely within your local bench instance using native Frappe ORM mechanisms. Standard Frappe Role Permissions Control (Role Permission Manager) governs who can read, write, or submit R&D proxies, ensuring laboratory sandbox data remains secure and restricted to R&D teams.
