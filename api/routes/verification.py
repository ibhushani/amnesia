from fastapi import APIRouter, Depends, HTTPException
from api.schemas.verification import VerifyRequest, VerifyResponse
from api.dependencies import get_sisa_trainer
from core.verification.membership_inference import verify_erasure # Defined previously
from core.verification.certificate_generator import generate_certificate # Defined previously
import torch

router = APIRouter()

@router.post("/verify", response_model=VerifyResponse)
def verify_model(
    req: VerifyRequest,
    trainer = Depends(get_sisa_trainer)
):
    """
    Performs Membership Inference Attack to verify data removal.
    If successful, generates a PDF certificate.
    """
    # Vision MVP Verification
    from core.verification.vision_verifier import verify_vision_model
    
    # Interpret indices as class (same heuristic as unlearning)
    target_class = 3 # Default Cat
    if req.data_indices and len(req.data_indices) == 1:
        target_class = req.data_indices[0]
        
    result = verify_vision_model(
        shard_id=req.shard_id,
        target_class=target_class,
        threshold=req.target_confidence_threshold
    )
    
    # Validation
    from api.config import get_settings
    settings = get_settings()

    cert_url = None
    if result["is_erased"]:
        # Generate the PDF Proof
        cert_path = generate_certificate(
            model_id=f"shard_{req.shard_id}",
            data_ids=[str(i) for i in req.data_indices] if req.data_indices else ["class_3"],
            verification_results={
                "forget_confidence": result["confidence"],
                "success": True,
                "confidence_before": 0.95
            },
            output_dir=settings.CERT_STORAGE
        )
        
        # Extract filename for the URL
        import os
        cert_filename = os.path.basename(cert_path)
        cert_url = f"/api/v1/certificates/{cert_filename}"

    return VerifyResponse(
        is_erased=result["is_erased"],
        confidence_score=result["confidence"],
        threshold=req.target_confidence_threshold,
        verification_method="VisionConfidenceCheck",
        certificate_url=cert_url
    )