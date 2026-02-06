"""
Dataset Upload & Management API
Handles CSV file uploads and dataset management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional
import pandas as pd
import shutil
import os
from datetime import datetime
from pydantic import BaseModel

from utils import get_logger

log = get_logger(__name__)

router = APIRouter()

# Storage configuration
DATA_DIR = Path("./data/uploads")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DatasetInfo(BaseModel):
    name: str
    filename: str
    rows: int
    columns: int
    size_bytes: int
    uploaded_at: str
    column_names: list


class DatasetListResponse(BaseModel):
    datasets: list[DatasetInfo]


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
):
    """
    Upload a CSV dataset for training.
    
    The CSV should have:
    - Feature columns (numerical)
    - A 'label' or 'target' column for classification
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Generate dataset name
    dataset_name = name or file.filename.replace('.csv', '')
    safe_name = "".join(c for c in dataset_name if c.isalnum() or c in '-_').lower()
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.csv"
    filepath = DATA_DIR / filename
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate and get info
        df = pd.read_csv(filepath)
        
        if df.empty:
            filepath.unlink()
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        info = DatasetInfo(
            name=safe_name,
            filename=filename,
            rows=len(df),
            columns=len(df.columns),
            size_bytes=filepath.stat().st_size,
            uploaded_at=timestamp,
            column_names=list(df.columns),
        )
        
        log.info(f"Dataset uploaded: {filename} ({len(df)} rows, {len(df.columns)} columns)")
        
        return {
            "success": True,
            "message": f"Dataset '{safe_name}' uploaded successfully",
            "dataset": info.model_dump(),
        }
        
    except pd.errors.EmptyDataError:
        if filepath.exists():
            filepath.unlink()
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    except Exception as e:
        if filepath.exists():
            filepath.unlink()
        log.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=DatasetListResponse)
async def list_datasets():
    """List all uploaded datasets"""
    datasets = []
    
    for filepath in DATA_DIR.glob("*.csv"):
        try:
            df = pd.read_csv(filepath, nrows=0)  # Just read headers
            stat = filepath.stat()
            
            # Parse timestamp from filename
            parts = filepath.stem.rsplit('_', 2)
            if len(parts) >= 3:
                uploaded_at = f"{parts[-2]}_{parts[-1]}"
                name = "_".join(parts[:-2])
            else:
                uploaded_at = datetime.fromtimestamp(stat.st_mtime).strftime("%Y%m%d_%H%M%S")
                name = filepath.stem
            
            # Count rows (fast method)
            with open(filepath, 'r') as f:
                row_count = sum(1 for _ in f) - 1  # Subtract header
            
            datasets.append(DatasetInfo(
                name=name,
                filename=filepath.name,
                rows=row_count,
                columns=len(df.columns),
                size_bytes=stat.st_size,
                uploaded_at=uploaded_at,
                column_names=list(df.columns),
            ))
        except Exception as e:
            log.warning(f"Could not read {filepath}: {e}")
    
    return DatasetListResponse(datasets=datasets)


@router.delete("/{filename}")
async def delete_dataset(filename: str):
    """Delete an uploaded dataset"""
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        filepath.unlink()
        log.info(f"Dataset deleted: {filename}")
        return {"success": True, "message": f"Dataset '{filename}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}/preview")
async def preview_dataset(filename: str, rows: int = 10):
    """Preview first N rows of a dataset"""
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        df = pd.read_csv(filepath, nrows=rows)
        return {
            "columns": list(df.columns),
            "data": df.to_dict(orient="records"),
            "total_rows": sum(1 for _ in open(filepath)) - 1,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
