import json
import pandas as pd

def check_field_order():
    # 1. Read Excel
    excel_path = 'project_docs/project_files/item_custom_field.xlsx'
    df = pd.read_excel(excel_path)
    
    # Extract fieldname from 'Item-fieldname'
    df['clean_fieldname'] = df['Name'].apply(lambda x: x.split('-')[-1] if '-' in str(x) else x)
    
    # 2. Read DocType JSON
    json_path = 'npd_management/npd_management/npd_management/doctype/npd_item/npd_item.json'
    with open(json_path) as f:
        data = json.load(f)
    
    fields = data.get('fields', [])
    
    # 3. Compare
    print(f"{'Sr':<5} | {'Excel Field':<30} | {'Current JSON Field':<30} | {'Status'}")
    print("-" * 80)
    
    max_len = max(len(df), len(fields))
    
    for i in range(max_len):
        excel_sr = i + 1
        excel_field = ""
        if i < len(df):
            excel_field = df.iloc[i]['clean_fieldname']
        
        json_field = ""
        if i < len(fields):
            json_field = fields[i].get('fieldname')
        
        status = "OK" if excel_field == json_field else "MISMATCH"
        
        print(f"{excel_sr:<5} | {excel_field:<30} | {json_field:<30} | {status}")

if __name__ == "__main__":
    check_field_order()
