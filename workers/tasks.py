"""
Celery Background Tasks
"""
import torch
import traceback
from typing import List, Dict, Any
from .celery_app import celery_app
from utils import get_logger

# Import Core Logic
from core.sisa.trainer import SISATrainer
from core.unlearning.gradient_ascent import constrained_unlearning
from data.dataset_manager import DatasetManager

log = get_logger(__name__)

# --- TRAINING TASKS ---

@celery_app.task(bind=True, name="workers.tasks.train_model_task")
def train_model_task(self, dataset_name: str, num_shards: int, epochs: int, model_type: str = "resnet"):
    """
    Background task to initialize SISA training.
    """
    task_id = self.request.id
    log.info(f"🚀 [Task {task_id}] Starting SISA Training for {dataset_name}...")

    try:
        # 1. Load Data
        dm = DatasetManager()
        # Ensure data is downloaded/ready
        dataset = dm.get_dataset(dataset_name, train=True, download=True)
        metadata = dm.get_metadata(dataset_name)

        # 2. Initialize Trainer
        trainer = SISATrainer(
            model_kwargs=metadata, # Pass input_shape/num_classes dynamically
            num_shards=num_shards,
            storage_path="./storage/models",
            device="auto"
        )

        # 3. Execute Training
        # Note: In a massive distributed system, we would spawn sub-tasks here.
        # For a single-node demo, we run the loop in this worker.
        results = trainer.train(
            dataset=dataset,
            epochs=epochs,
            batch_size=32
        )

        log.info(f"✅ [Task {task_id}] Training Complete.")
        return {"status": "completed", "results": results}

    except Exception as e:
        log.error(f"❌ [Task {task_id}] Training Failed: {str(e)}")
        log.error(traceback.format_exc())
        # Raise so Celery marks it as FAILURE
        raise e


# --- UNLEARNING TASKS ---

@celery_app.task(bind=True, name="workers.tasks.unlearn_task")
def unlearn_task(self, shard_id: int, forget_indices: List[int], alpha: float, epochs: int):
    """
    Background task to execute the 'Neural Eraser' on a specific shard.
    """
    task_id = self.request.id
    log.info(f"⚠️ [Task {task_id}] Starting Unlearning on Shard {shard_id}...")

    try:
        # 1. Initialize System
        # We need the trainer to access the specific shard model
        # Note: We re-initialize passing the existing storage path so it loads state
        trainer = SISATrainer(storage_path="./storage/models", num_shards=4) # Default shards, logic handles actual
        
        try:
            model = trainer.get_model_for_shard(shard_id)
            if model is None:
                model = trainer.load_model(shard_id) # Ensure it's loaded from disk
        except Exception:
            raise ValueError(f"Shard {shard_id} not found. Train the model first.")

        # 2. Data Surgery Setup
        # In a real app, we fetch the *actual* data points from the DB/Dataset using indices.
        # For this architectural demo, we simulate loading the shard's dataset.
        dm = DatasetManager()
        # Ideally, we should pass the dataset name in the task args. Defaulting to MNIST/CIFAR logic.
        # This is a simplification for the prototype.
        # In production: fetch 'dataset_name' from a Job DB using 'job_id'.
        full_dataset = dm.get_dataset("mnist", train=True, download=False) # Fallback default
        
        # 3. Create Masks (Forget vs Retain)
        # Get all data indices belonging to this shard
        all_shard_indices = trainer.shard_manager.get_data_indices_for_shard(shard_id)
        
        # Identify which local indices to forget
        # Logic: We need tensors. 
        # Ideally, 'forget_indices' are global IDs. Here we treat them as local subset indices for simplicity.
        subset = torch.utils.data.Subset(full_dataset, all_shard_indices)
        loader = torch.utils.data.DataLoader(subset, batch_size=len(subset))
        data, targets = next(iter(loader)) # Load all shard data into memory (careful with large data)

        # Create masks
        mask = torch.zeros(len(data), dtype=torch.bool)
        # Ensure indices are within bounds
        valid_indices = [i for i in forget_indices if i < len(data)]
        mask[valid_indices] = True

        x_forget = data[mask]
        x_retain = data[~mask]
        y_retain = targets[~mask]

        if len(x_forget) == 0:
            return {"status": "skipped", "message": "No valid data indices found to forget."}

        # 4. Run Gradient Ascent (The Core Algorithm)
        new_model = constrained_unlearning(
            model=model,
            x_forget=x_forget,
            x_retain=x_retain,
            y_retain=y_retain,
            alpha=alpha,
            epochs=epochs
        )

        # 5. Save the Cleaned Model
        trainer.save_shard_checkpoint(shard_id, new_model)

        log.info(f"✅ [Task {task_id}] Unlearning Complete for Shard {shard_id}")
        return {
            "status": "completed", 
            "shard_id": shard_id, 
            "forgotten_count": len(x_forget)
        }

    except Exception as e:
        log.error(f"❌ [Task {task_id}] Unlearning Failed: {str(e)}")
        log.error(traceback.format_exc())
        raise e