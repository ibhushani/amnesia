from fastapi import APIRouter
from api.schemas.unlearning import UnlearnRequest, UnlearnResponse
from workers.tasks import unlearn_task

router = APIRouter()

@router.post("/forget", response_model=UnlearnResponse)
def trigger_unlearning(req: UnlearnRequest):
    """
    Triggers the 'Neural Eraser' (Gradient Ascent) on a specific shard.
    """
    # Dispatch to Celery Worker
    task = unlearn_task.delay(
        shard_id=req.shard_id,
        forget_indices=req.data_indices,
        alpha=req.alpha,
        epochs=req.epochs
    )
    
    return UnlearnResponse(
        task_id=task.id,
        status="unlearning_started",
        shard_id=req.shard_id,
        data_removed_count=len(req.data_indices)
    )