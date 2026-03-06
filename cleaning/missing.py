import pandas as pd
import numpy as np

def intelligent_missing_handling(df: pd.DataFrame):

    report = {
        "numeric_filled_with_median": [],
        "categorical_filled_with_mode": [],
        "columns_flagged_high_missing": []
    }

    for col in df.columns:

        # Calculate missing percentage
        missing_ratio = df[col].isna().sum() / len(df)

        # 🚩 Flag if >70% missing
        if missing_ratio > 0.7:
            report["columns_flagged_high_missing"].append(col)
            continue  # Skip filling this column

        # Skip filling free‑text columns like notes, comments, remarks
        if any(x in col.lower() for x in ['notes', 'comment', 'remark', 'description']):
            continue

        # ==========================
        # Numeric Columns → Median
        # ==========================
        if pd.api.types.is_numeric_dtype(df[col]):

            if df[col].isna().sum() > 0:
                median_value = df[col].median()
                df[col] = df[col].fillna(median_value)
                report["numeric_filled_with_median"].append(col)

        # ==========================
        # Categorical Columns → Mode
        # ==========================
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col]):

            if df[col].isna().sum() > 0:
                mode_series = df[col].mode()

                if not mode_series.empty:
                    mode_value = mode_series[0]
                    df[col] = df[col].fillna(mode_value)
                    report["categorical_filled_with_mode"].append(col)

    return df, report