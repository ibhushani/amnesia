from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from api.schemas.training import TrainingRequest, TrainingResponse
from workers.tasks import train_model_task # We will define this later in workers/
from utils.helpers import generate_uuid

router = APIRouter()

@router.post("/train", response_model=TrainingResponse)
def trigger_training(
    req: TrainingRequest, 
    background_tasks: BackgroundTasks
):
    """
    Initiates SISA training.
    Dispatches jobs to Celery workers for parallel processing.
    """
    job_id = generate_uuid()
    
    # In a real deployment, we would split the dataset here 
    # and dispatch N tasks, one for each shard.
    # For simplicity, we dispatch one orchestrator task.
    
    # Run locally for Vision MVP
    background_tasks.add_task(
        train_model_task,
        dataset_name=req.dataset_name,
        num_shards=req.num_shards,
        epochs=req.epochs,
        model_type=req.model_type
    )
    
    # Dummy task ID since we aren't using Celery
    mock_id = f"local-{job_id}"
    
    return TrainingResponse(
        task_id=mock_id,
        status="dispatched",
        message="Training job started in background.",
        shards_created=req.num_shards
    )