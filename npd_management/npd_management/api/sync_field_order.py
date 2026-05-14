import json

def sync_field_order():
    prod_path = 'project_docs/production_item_doctype.json'
    local_path = 'npd_management/npd_management/npd_management/doctype/npd_item/npd_item.json'
    
    with open(prod_path) as f:
        prod_data = json.load(f)
    
    with open(local_path) as f:
        local_data = json.load(f)
        
    prod_fields = prod_data.get('fields', [])
    local_fields = local_data.get('fields', [])
    
    # Map local fields by fieldname for quick lookup
    local_fields_map = {f.get('fieldname'): f for f in local_fields}
    
    new_fields = []
    seen_fieldnames = set()
    
    # 1. Follow production order
    for f in prod_fields:
        fname = f.get('fieldname')
        if fname in local_fields_map:
            new_fields.append(local_fields_map[fname])
            seen_fieldnames.add(fname)
        else:
            # If a field exists in production but not locally, should we skip it?
            # For now, yes, because we only want to reorder what we have.
            # But wait! If it's a standard field, it SHOULD be there.
            pass
            
    # 2. Append local fields that are NOT in production
    for f in local_fields:
        fname = f.get('fieldname')
        if fname not in seen_fieldnames:
            new_fields.append(f)
            
    # Update indices (idx)
    for i, f in enumerate(new_fields):
        f['idx'] = i + 1
        
    local_data['fields'] = new_fields
    
    # Save back
    with open(local_path, 'w') as f:
        json.dump(local_data, f, indent=1)
        
    print(f"Synced {len(new_fields)} fields in NPD Item.")

if __name__ == "__main__":
    sync_field_order()
