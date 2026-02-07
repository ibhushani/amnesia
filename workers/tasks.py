"""
Worker tasks for Amnesia (Modified for Vision MVP)
"""
import os
import shutil
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from utils import get_logger

# Import Vision MVP Logic
from core.unlearning.simple_unlearn import unlearn_class

log = get_logger(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
STORAGE_DIR = os.path.join(BASE_DIR, 'storage', 'models')

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)

# Map dataset names to IDs/paths
DATASET_MAP = {
    "mnist": "mnist",
    "cifar10": "cifar10",
    "custom": "custom"
}

async def train_model_task(dataset_name: str, num_shards: int, epochs: int, model_type: str = "resnet"):
    """
    Vision MVP: Simulates training by loading the pre-trained CIFAR-10 model.
    """
    task_id = "local_train_job"
    log.info(f"🚀 [Task {task_id}] Starting Vision MVP Training (Setup) for {dataset_name}...")

    try:
        if dataset_name == "cifar10" or dataset_name == "custom":
            # 1. Check if we have the base model
            base_model_path = os.path.join(MODELS_DIR, "resnet18_cifar10_base.pth")
            
            if not os.path.exists(base_model_path):
                log.warning(f"⚠️ Base model not found at {base_model_path}. Please run scripts/setup_cifar.py first.")
                return {"status": "failed", "error": "Base model missing"}

            # 2. "Train" by copying the base model to the shard locations
            # In SISA, we have N shards. For MVP, we just copy it to shard_0 (the one we'll unlearn).
            target_path = os.path.join(STORAGE_DIR, "shard_0.pth")
            shutil.copy(base_model_path, target_path)
            
            log.info(f"✅ [Task {task_id}] 'Training' complete. Model deployed to {target_path}")
            return {"status": "completed", "model_path": target_path}
            
        else:
            log.info(f"Using legacy/dummy training for {dataset_name}")
            return {"status": "completed", "message": "Dummy training done"}

    except Exception as e:
        log.error(f"❌ Training Failed: {e}")
        return {"status": "failed", "error": str(e)}


async def unlearn_task(shard_id: int, forget_indices: list, alpha: float, epochs: int):
    """
    Vision MVP: Executes Gradient Ascent on Class 3 (Cat) or specified indices.
    """
    task_id = "local_unlearn_job"
    log.info(f"🧹 [Task {task_id}] Starting Vision Unlearning on Shard {shard_id}...")

    try:
        # 1. Load the Model
        model_path = os.path.join(STORAGE_DIR, f"shard_{shard_id}.pth")
        if not os.path.exists(model_path):
             log.error("Model not found. Please 'Train' first.")
             return {"status": "failed", "error": "Model not found"}

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load ResNet-18 structure
        from torchvision.models import resnet18
        model = resnet18(weights=None) # Structure only
        model.fc = nn.Linear(512, 10) # 10 classes
        
        # Load weights safely
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model.to(device)
        
        # 2. Load Data (CIFAR-10)
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        # Use a subset for speed in demo
        dataset = datasets.CIFAR10(root=DATA_DIR, train=True, download=True, transform=transform)
        # Just use first 500 images for the demo speed
        subset = torch.utils.data.Subset(dataset, range(500)) 
        loader = torch.utils.data.DataLoader(subset, batch_size=32, shuffle=True)
        
        # 3. Interpret "Forget Indices"
        # If user provides [3], assume we want to forget CLASS 3 (Cats)
        # If user provides [0, 1, 2], assume indices (but we'll just defatul to class 3 for the demo impact)
        target_class = 3 # Default to Cat
        
        if forget_indices and len(forget_indices) == 1:
             # Heuristic: if single index, treat as class
             target_class = forget_indices[0] 
        
        log.info(f"🐱 Target Class to Forget: {target_class}")

        # 4. Optimizer
        # Scale Alpha from UI (1-10) to Learning Rate (0.001 - 0.01)
        learning_rate = alpha * 0.001
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

        # 5. Run Unlearning (The Toy Code)
        log.info(f"Running for {epochs} epochs with LR={learning_rate}...")
        for _ in range(epochs):
            unlearn_class(model, loader, target_class_index=target_class, optimizer=optimizer, device=device)
        
        # 6. Save result
        # Overwrite or save as new? Let's overwrite for the demo simplicity so verification checks this one
        torch.save(model.state_dict(), model_path)
        log.info("✅ Unlearned model saved.")
        
        return {"status": "completed", "class_forgotten": target_class}

    except Exception as e:
        log.error(f"❌ Unlearning Failed: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}