from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import uuid
from cleaning.structural import structural_cleaning

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse(open("templates/index.html", encoding="utf-8").read())


@app.post("/clean")
async def clean_data(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    # 🔥 Use structural module
    df, structural_report = structural_cleaning(df)

    output_file = f"outputs/cleaned_{uuid.uuid4()}.csv"
    df.to_csv(output_file, index=False)

    return FileResponse(
        output_file,
        filename="cleaned_data.csv",
        headers={
            "X-Duplicates-Removed": str(structural_report["duplicates_removed"])
        }
    )