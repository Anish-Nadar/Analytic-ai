import pandas as pd
import re

def structural_cleaning(df: pd.DataFrame):

    report = {}

    # ==============================
    # Phase A – Basic Structural Fixes
    # ==============================

    # Remove duplicates
    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()
    report["duplicates_removed"] = int(duplicate_count)

    # Remove fully empty rows
    r_before = len(df)
    df = df.dropna(how='all')
    report["empty_rows_removed"] = int(r_before - len(df))

    # Remove fully empty columns
    cols_before = df.shape[1]
    df = df.dropna(axis=1, how='all')
    report["empty_columns_removed"] = int(cols_before - df.shape[1])

    # Standardize column names
    original_cols = df.columns.tolist()
    df.columns = [re.sub(r'\W+', '_', col.strip().lower()) for col in df.columns]
    report["column_names_standardized"] = True
    report["original_columns"] = original_cols
    report["new_columns"] = df.columns.tolist()

    # Trim whitespace
    object_cols = df.select_dtypes(include=['object']).columns
    if len(object_cols) > 0:
        for col in object_cols:
            df[col] = df[col].astype(str).str.strip()
        report["whitespace_trimmed"] = True
    else:
        report["whitespace_trimmed"] = False

    # ==============================
    # Phase B – Type Correction
    # ==============================

    report["numeric_converted"] = []
    report["datetime_converted"] = []
    report["boolean_converted"] = []

    for col in df.columns:

        if df[col].dtype == "object":

            # Try numeric conversion
            numeric_try = pd.to_numeric(df[col], errors="coerce")
            if numeric_try.notna().sum() >= len(df) * 0.8:
                df[col] = numeric_try
                report["numeric_converted"].append(col)
                continue

            # Try datetime conversion
            datetime_try = pd.to_datetime(df[col], errors="coerce")
            if datetime_try.notna().sum() >= len(df) * 0.8:
                df[col] = datetime_try
                report["datetime_converted"].append(col)
                continue

            # Try boolean conversion
            lower_vals = df[col].str.lower().dropna().unique()
            bool_map = {
                "true": True,
                "false": False,
                "yes": True,
                "no": False,
                "1": True,
                "0": False
            }

            if len(lower_vals) > 0 and set(lower_vals).issubset(bool_map.keys()):
                df[col] = df[col].str.lower().map(bool_map)
                report["boolean_converted"].append(col)

    return df, report