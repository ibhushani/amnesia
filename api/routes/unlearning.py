from fastapi import APIRouter, BackgroundTasks
from api.schemas.unlearning import UnlearnRequest, UnlearnResponse
from workers.tasks import unlearn_task

router = APIRouter()

@router.post("/forget", response_model=UnlearnResponse)
def trigger_unlearning(req: UnlearnRequest, background_tasks: BackgroundTasks):
    """
    Triggers the 'Neural Eraser' (Gradient Ascent) on a specific shard.
    """
    # Dispatch locally for Vision MVP
    background_tasks.add_task(
        unlearn_task,
        shard_id=req.shard_id,
        forget_indices=req.data_indices,
        alpha=req.alpha,
        epochs=req.epochs
    )
    
    mock_id = f"local-unlearn-{req.shard_id}"
    
    return UnlearnResponse(
        task_id=mock_id,
        status="unlearning_started",
        shard_id=req.shard_id,
        data_removed_count=len(req.data_indices)
    )