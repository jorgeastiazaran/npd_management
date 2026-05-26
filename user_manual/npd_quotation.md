# NPD Quotation

Before moving a product to full production, R&D and sales teams may need to simulate pricing and prepare pre-commercial quotes for potential clients. The `NPD Quotation` document enables you to send professional proposals for experimental items while keeping them isolated from live financial cycles.

---

## 1. Creating an NPD Quotation

### Step-by-Step Instructions:

1. Navigate to **NPD Quotation** list view and click **Add NPD Quotation**.
2. Select the target **Customer** (standard ERPNext Customer master list) or enter a prospect's name.
3. In the items table:
   - Select the target **NPD Item** to quote.
   - Enter quantity and rate.
   - The system retrieves estimated costs from the linked `NPD BOM` to calculate margin percentages.
4. Set tax templates and terms if needed.
5. Save the document.

---

## 2. Transitioning to Standard Quotation

If the client approves the pre-commercial quote, and the `NPD Item` is promoted to a standard `Item`, you can convert the quotation to a standard production Quotation:

1. Promote the source **NPD Item** to a standard **Item** (see the [NPD Item Guide](npd_item.md)).
2. Open the original **NPD Quotation** document.
3. Click the **Create Standard Quotation** button in the header.
4. The system automatically creates a standard ERPNext **Quotation** document, mapping the customer and converting the sandbox items to the newly promoted standard items.
5. Save and submit the standard Quotation to initiate the standard sales pipeline.
