from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import pandas as pd
import uuid
import os

from cleaning.structural import structural_cleaning
from cleaning.missing import intelligent_missing_handling
from cleaning.quality import data_quality_checks

app = FastAPI()

# Ensure outputs folder exists
os.makedirs("outputs", exist_ok=True)


@app.get("/")
def home():
    try:
        return HTMLResponse(open("templates/index.html", encoding="utf-8").read())
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "index.html not found in templates folder"}
        )


@app.post("/clean")
async def clean_data(file: UploadFile = File(...)):
    try:
        # Read CSV
        df = pd.read_csv(file.file)

        # Phase A – Structural Cleaning
        df, structural_report = structural_cleaning(df)

        # Phase C – Intelligent Missing Handling
        df, missing_report = intelligent_missing_handling(df)
        #Phase D – Data Quality Checks & Outlier Removal
        df, quality_report = data_quality_checks(df, remove_outliers=True)

        # Save cleaned file
        output_file = f"outputs/cleaned_{uuid.uuid4()}.csv"
        df.to_csv(output_file, index=False)

        return FileResponse(
            path=output_file,
            filename="cleaned_data.csv",
            headers={
                "X-Duplicates-Removed": str(structural_report.get("duplicates_removed", 0)),
                "X-Empty-Rows-Removed": str(structural_report.get("empty_rows_removed", 0)),
                "X-Empty-Columns-Removed": str(structural_report.get("empty_columns_removed", 0)),
                "X-Numeric-Filled": str(len(missing_report.get("numeric_filled_with_median", []))),
                "X-Categorical-Filled": str(len(missing_report.get("categorical_filled_with_mode", []))),
                "X-High-Missing-Columns": ",".join(
                    missing_report.get("columns_flagged_high_missing", [])
                )
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )