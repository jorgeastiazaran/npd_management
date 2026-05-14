# NPD Management — ERPNext Product Lifecycle Sandbox

An advanced, fully integrated **New Product Development (NPD)** module built for ERPNext and the Frappe Framework. 

This application introduces a secure **R&D Sandbox Testing Layer** that perfectly mirrors your active production inventory structures while operating in total isolation from the financial master ledger. Formulators, laboratory engineers, and trial managers can design multi-level experimental formulations (`NPD BOM`), simulate manufacturing production orders (`NPD Trial`), execute experimental sourcing RFQs, and apply strict quality inspection matrices without cluttering your core enterprise item catalogs or impacting live accounting valuations.

---

## 🏗️ Repository Architecture

This repository is organized as a fully self-contained deployment suite containing both the core application code and the automated dynamic schema mirroring tools:

```text
├── npd_management/            # Core Frappe Custom Application code
├── install_customized.py      # Automated Interactive Deployment Console wrapper
├── extract_doctypes.py        # Dynamic Universal REST Schema Extractor engine
├── finalize_doctypes.py       # R&D Structure & Options relinking logic
├── project_docs/              # Complete Architectural Briefs & Specifications
├── setup_test_site.sh         # Local Docker sandbox spin-up utility
└── docker-compose.yml         # Containerized dev infrastructure blueprint
```

### Core Application Components (`npd_management/`)
* **Interactive Promotion Engine**: Frontend routing automation (`npd_item.js`) that safely sanitizes experimental prototypes and launches standard pre-filled production `Item` forms for final naming series selection.
* **Two-Way Synchronization Hooks**: Background listeners (`hooks.py`) that monitor standard catalog commitments to automatically map promotion records back to original sandbox items.
* **Pure Local Execution ORM**: Optimized API utility layers (`npd_utils.py`) that dynamically read and commit local MariaDB database records directly, guaranteeing zero latency.

---

## 🚀 Installation Guide for External ERPNext Instances

Because every enterprise customizes their operational master records (`Item`, `BOM`, `Work Order`, `Quality Inspection`, `Supplier`, `Quotation`) with unique internal fields and mandatory toggles, the custom application dynamically mirrors all of these standard layouts directly into their counterpart **NPD proxy schemas** (`NPD Item`, `NPD BOM`, `NPD Trial`, `NPD Quality Inspection`, `NPD Supplier`, `NPD Quotation`) precisely *before* final installation. This guarantees absolute structural parity and zero runtime upgrade conflicts.

We provide a streamlined, automated deployment console script to orchestrate this end-to-end mapping seamlessly.

### Prerequisites
1. Access to a terminal within your active host server or bench container.
2. An **API Key and API Secret** generated for a user with **System Administrator** access on your target ERPNext instance.
   > **Note on API Usage**: The API keys are utilized strictly as a **one-time pre-installation setup mechanism** by our external tailoring script to extract your site's custom layout structures over local REST. Once successfully compiled and installed, the application core drops all API reliance and operates **100% locally** via native MariaDB database transactions.

### Deployment Instructions

#### 1. Clone the Repository
Clone this package directly into your local deployment environment:
```bash
git clone https://github.com/your-org/npd_erpnext.git
cd npd_erpnext
```

#### 2. Launch the Automated Custom Installer
Execute the self-contained installation console utility:
```bash
python3 install_customized.py
```

#### 3. Choose Your Synchronization Mode
The script will present a choice between two explicit mapping methods:
* **Option 1: Automated Live Sync**  
  Prompts for your Target Site Name, local instance URL, and one-time Administrator API Credentials to programmatically extract active layout metadata (`tabCustom Field` overlays + `tabProperty Setter` properties) over the network.
* **Option 2: Offline CSV Template Import**  
  Allows bypassing network API loops entirely. You simply download your field layout as a CSV file natively via Frappe's pre-sorted **"Customize Form"** view and save it to `project_docs/project_files/item layout.csv`. The installer parses rows sequentially, maps headers flexibly, auto-hashes layout breaks, and merges your R&D layout additively over the base package structure.

#### 4. Automated Execution
Once your synchronization path is complete, the console wrapper programmatically executes:
1. **Schema Compilation**: Merges standard definitions with active layout properties while enforcing a rigorous metadata preservation policy (retaining hidden attributes like `unique`, `allow_on_submit`, `translatable`, and unlisted base fields).
2. **Finalization & Mapping**: Injects custom experimental calculation sections (Costing Matrices, Nutritional Breakdowns) and automatically rewires parent-child layout relationships (`NPD BOM` child items).
3. **Native Installation**: Executes the native bench application framework commit (`bench --site [site_name] install-app npd_management`) directly into your database.

---

## 🔒 Pure Local Operation Mode
Once successfully deployed, the application automatically drops all remote API connection loops. It operates directly as a standard, natively installed Frappe Custom App inside your local instance, reading and executing standard ORM instructions natively under role-based user access controls.

---

## 📚 Detailed Documentation
For deep technical deep-dives into multi-level costing evaluation logic, nutritional rollup abstractions, and database entity decoupling schemas, review the full design brief:
👉 [**Project Design Brief & Architecture**](project_docs/project_brief.md)
