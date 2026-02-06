from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from api.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/{filename}")
def download_certificate(filename: str):
    """
    Download the generated PDF certificate.
    """
    # Security: Ensure we only look in the cert directory
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.CERT_STORAGE, safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    return FileResponse(
        file_path, 
        media_type='application/pdf', 
        filename=safe_filename
    )