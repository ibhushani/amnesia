from pydantic import BaseModel
from typing import List, Optional

class VerifyRequest(BaseModel):
    shard_id: int
    data_indices: List[int]
    target_confidence_threshold: float = 0.6

class VerifyResponse(BaseModel):
    is_erased: bool
    confidence_score: float
    threshold: float
    verification_method: str
    certificate_url: Optional[str] = None