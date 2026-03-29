import pandas as pd
import numpy as np

def clean_and_detect(file_path: str):
    # Read the file
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    initial_rows = len(df)
    
    # --- 1. Clean Data ---
    # Drop rows/columns that are completely empty
    df.dropna(how='all', inplace=True)
    df.dropna(how='all', axis=1, inplace=True)
    
    # Drop exact duplicates
    duplicates_removed = int(df.duplicated().sum())
    df.drop_duplicates(inplace=True)
    
    # Handle missing values smartly
    nulls_fixed = int(df.isna().sum().sum())
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna('Unknown')
            
    final_rows = len(df)
    rows_dropped = initial_rows - final_rows
    
    # --- 2. Heuristic Column Detection ---
    detected_columns = {
        "Date": None,
        "Revenue": None,
        "Product": None
    }
    
    date_keywords = ['date', 'time', 'created', 'day', 'month', 'year']
    revenue_keywords = ['revenue', 'sale', 'price', 'amount', 'total', 'cost', 'spend']
    product_keywords = ['product', 'item', 'name', 'category', 'sku']
    
    cols_lower = [str(c).lower() for c in df.columns]
    
    # Date
    for col, lower in zip(df.columns, cols_lower):
        if any(keyword in lower for keyword in date_keywords):
            detected_columns["Date"] = col
            try:
                # Convert to standard string format to be JSON serializable
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                df[col] = df[col].fillna('Unknown')
            except:
                pass
            break
            
    # Revenue (Requires numeric type after cleaning)
    for col, lower in zip(df.columns, cols_lower):
        if any(keyword in lower for keyword in revenue_keywords) and pd.api.types.is_numeric_dtype(df[col]):
            detected_columns["Revenue"] = col
            break
            
    # Product
    for col, lower in zip(df.columns, cols_lower):
        if any(keyword in lower for keyword in product_keywords):
            detected_columns["Product"] = col
            break
    
    # Results
    cleaned_json = df.to_json(orient='records')
    preview_data = df.head(10).to_dict(orient='records')
    columns_list = df.columns.tolist()
    
    return {
        "stats": {
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "rows_dropped": int(rows_dropped),
            "duplicates_removed": duplicates_removed,
            "nulls_fixed": nulls_fixed
        },
        "detected_columns": detected_columns,
        "columns": columns_list,
        "preview": preview_data,
        "cleaned_data_json": cleaned_json
    }
