# NPD Sourcing (RFQ & Supplier Quotation)

When formulating new food products, you may need to source new ingredients, packaging, or additives from external vendors. To prevent cluttering your live procurement lists and vendor database, the NPD Sandbox includes isolated procurement proxy tools.

---

## 1. NPD Supplier

An `NPD Supplier` is a vendor record stored in the R&D sandbox. It exists independently of your standard production Supplier master list.
- Use `NPD Supplier` to store contact info, certifications, and lead times for research-only vendors.
- Standard purchase cycles cannot access `NPD Suppliers`.

---

## 2. NPD RFQ (Request for Quotation)

To query suppliers for pricing, specifications, and lead times of experimental ingredients, use the `NPD RFQ` document.

### Step-by-Step Instructions:

1. Navigate to **NPD RFQ** and click **Add NPD RFQ**.
2. Set the **Required Date** and target **NPD Items**.
3. In the **Suppliers** child table, add one or more **NPD Suppliers**.
4. Save the document.
5. Use standard print templates to email the RFQ details directly to the vendors.

---

## 3. NPD Supplier Quotation

When a vendor replies with pricing or ingredient specification data sheets, log the response using an `NPD Supplier Quotation`.

### Creating an NPD Supplier Quotation:

1. Open the source **NPD RFQ** document.
2. Click the **Create Supplier Quotation** action button.
3. Select the responding **NPD Supplier**.
4. In the items table:
   - Verify/update the price rate.
   - Enter lead times and minimum order quantities (MOQ).
5. Save the document.

> [!NOTE]
> Saving the `NPD Supplier Quotation` updates the estimated ingredient costing fields in the formulation engine, allowing your `NPD BOM` to compute accurate, up-to-date costing projections.
