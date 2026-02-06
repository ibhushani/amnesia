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
    
    task = train_model_task.delay(
        dataset_name=req.dataset_name,
        num_shards=req.num_shards,
        epochs=req.epochs,
        model_type=req.model_type
    )
    
    return TrainingResponse(
        task_id=task.id,
        status="dispatched",
        message="Training job started in background.",
        shards_created=req.num_shards
    )