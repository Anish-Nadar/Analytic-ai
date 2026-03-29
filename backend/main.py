from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io
import json
import os
import shutil

import models
from database import engine, get_db
import data_processor
import metrics_engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Data Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Data Analyst API"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Create dummy user if not exists for demo purposes
    user = db.query(models.User).filter_by(email="demo@user.com").first()
    if not user:
        user = models.User(email="demo@user.com")
        db.add(user)
        db.commit()
        db.refresh(user)

    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save to db
    new_upload = models.Upload(filename=file.filename, file_path=file_path, user_id=user.id)
    db.add(new_upload)
    db.commit()
    db.refresh(new_upload)

    # Parse data for quick preview using pandas
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Take first 10 rows for preview
        preview_data = json.loads(df.head(10).to_json(orient="records"))
        columns = df.columns.tolist()

        return {"filename": file.filename, "upload_id": new_upload.id, "columns": columns, "preview": preview_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/clean/{upload_id}")
def clean_data(upload_id: int, db: Session = Depends(get_db)):
    upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
        
    try:
        # Run the cleaning and detection process
        results = data_processor.clean_and_detect(upload.file_path)
        
        # Save to ProcessedData table
        existing_processed = db.query(models.ProcessedData).filter(models.ProcessedData.upload_id == upload_id).first()
        if existing_processed:
            existing_processed.cleaned_data_json = results['cleaned_data_json']
        else:
            new_processed = models.ProcessedData(
                upload_id=upload_id,
                cleaned_data_json=results['cleaned_data_json']
            )
            db.add(new_processed)
        
        db.commit()
        
        # We don't want to send the full cleaned JSON back in the HTTP response body to save bandwidth, 
        # so we pop it out.
        results.pop('cleaned_data_json')
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning data: {str(e)}")

class MetricsRequest(BaseModel):
    metadata_columns: dict

@app.post("/metrics/{upload_id}")
def generate_metrics(upload_id: int, request: MetricsRequest, db: Session = Depends(get_db)):
    processed = db.query(models.ProcessedData).filter(models.ProcessedData.upload_id == upload_id).first()
    if not processed:
        raise HTTPException(status_code=404, detail="Cleaned data not found.")
        
    try:
        results = metrics_engine.compute_metrics(processed.cleaned_data_json, request.metadata_columns)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing metrics: {str(e)}")
