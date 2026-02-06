from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TrainingRequest(BaseModel):
    dataset_name: str = Field(..., description="Name of dataset (e.g., 'cifar10', 'mnist')")
    model_type: str = Field("resnet", description="Architecture to use")
    num_shards: int = Field(4, ge=1, le=20)
    epochs: int = Field(5, ge=1)
    batch_size: int = 32

class TrainingResponse(BaseModel):
    task_id: str
    status: str
    message: str
    shards_created: int