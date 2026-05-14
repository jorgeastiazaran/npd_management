import json

def reconstruct_and_sync():
    # 1. Load data
    with open('project_docs/production_item_doctype.json') as f:
        prod_doc = json.load(f)
    with open('project_docs/production_custom_fields.json') as f:
        custom_fields = json.load(f)
    with open('npd_management/npd_management/npd_management/doctype/npd_item/npd_item.json') as f:
        local_doc = json.load(f)

    # 2. Reconstruct production order
    # Start with standard fields
    fields_order = [f.get('fieldname') for f in prod_doc.get('fields', [])]
    
    # We need to insert custom fields.
    # Since insert_after might point to a field not yet in fields_order, we iterate.
    to_insert = custom_fields[:]
    max_iters = 100
    while to_insert and max_iters > 0:
        max_iters -= 1
        inserted_this_round = []
        for cf in to_insert:
            after = cf.get('insert_after')
            fname = cf.get('fieldname')
            if not after:
                # If no insert_after, append to end
                fields_order.append(fname)
                inserted_this_round.append(cf)
            elif after in fields_order:
                idx = fields_order.index(after)
                fields_order.insert(idx + 1, fname)
                inserted_this_round.append(cf)
        
        for cf in inserted_this_round:
            to_insert.remove(cf)
            
    if to_insert:
        print(f"Warning: Could not insert {len(to_insert)} fields due to missing 'insert_after' targets.")
        # Just append them
        for cf in to_insert:
            fields_order.append(cf.get('fieldname'))

    # 3. Sync local NPD Item
    local_fields = local_doc.get('fields', [])
    local_fields_map = {f.get('fieldname'): f for f in local_fields}
    
    new_fields = []
    seen = set()
    for fname in fields_order:
        if fname in local_fields_map:
            new_fields.append(local_fields_map[fname])
            seen.add(fname)
            
    # Append any local-only fields
    for f in local_fields:
        if f.get('fieldname') not in seen:
            new_fields.append(f)
            
    # Update idx
    for i, f in enumerate(new_fields):
        f['idx'] = i + 1
        
    local_doc['fields'] = new_fields
    
    with open('npd_management/npd_management/npd_management/doctype/npd_item/npd_item.json', 'w') as f:
        json.dump(local_doc, f, indent=1)
        
    print(f"Successfully reconstructed and synced {len(new_fields)} fields.")

if __name__ == "__main__":
    reconstruct_and_sync()
