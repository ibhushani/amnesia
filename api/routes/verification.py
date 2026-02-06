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
    try:
        model = trainer.get_model_for_shard(req.shard_id)
        if not model:
            # Try to load it if not in memory
            model = trainer.load_shard(req.shard_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Shard {req.shard_id} not found or not trained.")

    # Mock Data Generation for Verification (In prod, fetch specific rows from DB)
    # We use random data here to simulate the check against the 'forget set'
    torch.manual_seed(req.shard_id) 
    # NOTE: In a real app, you must load the EXACT same data points that were deleted.
    # Here we mock it for the architectural demo.
    x_target = torch.randn(len(req.data_indices), 10) # Adjust dim based on model
    y_target = torch.randint(0, 2, (len(req.data_indices),))

    # Run MIA
    result = verify_erasure(
        model=model, 
        x_target=x_target, 
        y_target=y_target, 
        threshold=req.target_confidence_threshold
    )
    
    cert_url = None
    if result["is_erased"]:
        # Generate the PDF Proof
        cert_path = generate_certificate(
            job_id=f"verif_{req.shard_id}",
            confidence_score=result["confidence"],
            is_compliant=True
        )
        cert_url = f"/api/v1/certificates/{req.shard_id}.pdf"

    return VerifyResponse(
        is_erased=result["is_erased"],
        confidence_score=result["confidence"],
        threshold=req.target_confidence_threshold,
        verification_method="MembershipInferenceAttack",
        certificate_url=cert_url
    )