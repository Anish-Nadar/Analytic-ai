import pandas as pd
import numpy as np

def data_quality_checks(df: pd.DataFrame, remove_outliers: bool = True):

    report = {
        "constant_columns_removed": [],
        "high_cardinality_columns_removed": [],
        "high_missing_columns_removed": [],
        "outliers_detected": {},
        "outliers_removed": {}
    }

    # ==========================
    # 1️⃣ Remove Constant Columns
    # ==========================
    for col in df.columns:
        if df[col].nunique(dropna=False) == 1:
            report["constant_columns_removed"].append(col)
            df = df.drop(columns=[col])

    # ==========================
    # 2️⃣ Remove High Cardinality (Categorical)
    # ==========================
    cols_to_drop = []
    for col in df.select_dtypes(include=["object", "category"]):
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.5:
            report["high_cardinality_columns_removed"].append(col)
            cols_to_drop.append(col)
    df = df.drop(columns=cols_to_drop)

    # ==========================
    # 3️⃣ Remove High Missing Columns (>70% missing)
    # ==========================
    cols_to_drop = []
    for col in df.columns:
        missing_ratio = df[col].isna().sum() / len(df)
        if missing_ratio > 0.7:
            report["high_missing_columns_removed"].append(col)
            cols_to_drop.append(col)
    df = df.drop(columns=cols_to_drop)

    # ==========================
    # 4️⃣ Outlier Detection (IQR)
    # ==========================
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

        report["outliers_detected"][col] = int(len(outliers))

        if remove_outliers and len(outliers) > 0:
            before_rows = len(df)
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            removed_rows = before_rows - len(df)
            report["outliers_removed"][col] = int(removed_rows)

    return df, report