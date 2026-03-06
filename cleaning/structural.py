import pandas as pd
import re

def structural_cleaning(df: pd.DataFrame):

    report = {}

    # ==============================
    # Phase A – Basic Structural Fixes
    # ==============================

    # Remove duplicates
    # first normalise any literal string "nan" etc. so pandas treats them as
    # missing when we compute duplicates or later fill values
    df = df.replace(["nan", "NaN", "None"], pd.NA)

    # drop duplicates based on all columns except free‑text fields such as notes
    # so that rows differing only in commentary are considered duplicates.
    subset_cols = None
    text_cols = [c for c in df.columns if c.lower().startswith("notes")]
    if text_cols:
        subset_cols = [c for c in df.columns if c not in text_cols]

    duplicate_count = df.duplicated(subset=subset_cols).sum()
    df = df.drop_duplicates(subset=subset_cols)
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

    # Trim whitespace in object columns without converting NaN into string
    object_cols = df.select_dtypes(include=['object']).columns
    if len(object_cols) > 0:
        for col in object_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
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

            s = df[col].astype(str).str.strip()

            # Skip numeric conversion for columns that are clearly IDs or codes
            is_id_col = any(x in col.lower() for x in ['id', 'code', 'key'])

            # boolean conversion – map most common boolean‑like tokens
            bool_map = {
                "true": True,
                "false": False,
                "yes": True,
                "no": False,
                "1": True,
                "0": False,
                "y": True,
                "n": False,
            }
            mapped_bool = s.str.lower().map(bool_map)
            if mapped_bool.notna().sum() >= len(df) * 0.5:
                df[col] = mapped_bool
                report["boolean_converted"].append(col)
                continue

            # numeric conversion – skip ID columns; strip non‑digits for others
            if not is_id_col:
                numeric_try = pd.to_numeric(s.str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce")
                if numeric_try.notna().sum() >= len(df) * 0.5:
                    df[col] = numeric_try
                    report["numeric_converted"].append(col)
                    continue

            # datetime conversion – require 50% parseable; if <50%, leave as string
            datetime_try = pd.to_datetime(s, errors="coerce")
            if datetime_try.notna().sum() >= len(df) * 0.5:
                df[col] = datetime_try.dt.strftime('%Y-%m-%d')
                report["datetime_converted"].append(col)
                continue

    return df, report