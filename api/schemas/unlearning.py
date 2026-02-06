from pydantic import BaseModel, Field
from typing import List

class UnlearnRequest(BaseModel):
    shard_id: int = Field(..., description="The ID of the shard containing the data")
    data_indices: List[int] = Field(..., description="List of data indices to forget")
    alpha: float = Field(10.0, description="Forgetting strength (Gradient Ascent step)")
    epochs: int = Field(50, description="Number of unlearning steps")

class UnlearnResponse(BaseModel):
    task_id: str
    status: str
    shard_id: int
    data_removed_count: int