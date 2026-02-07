
import os
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
from utils import get_logger

log = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STORAGE_DIR = os.path.join(BASE_DIR, 'storage', 'models')

def verify_vision_model(shard_id: int, target_class: int = 3, threshold: float = 0.5):
    """
    Verifies if the model has forgotten the target class (Vision MVP).
    """
    try:
        log.info(f"🔍 Verifying Shard {shard_id} for Class {target_class}...")
        
        # 1. Load Model
        model_path = os.path.join(STORAGE_DIR, f"shard_{shard_id}.pth")
        if not os.path.exists(model_path):
            log.error("Model file not found.")
            return {"confidence": 1.0, "is_erased": False, "error": "Model not found"}

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        from torchvision.models import resnet18
        model = resnet18(weights=None)
        model.fc = nn.Linear(512, 10)
        
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()

        # 2. Load Target Data (Images of the class we supposedly forgot)
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        
        # Download/Load CIFAR-10 Test Set
        dataset = datasets.CIFAR10(root=DATA_DIR, train=False, download=True, transform=transform)
        
        # Filter for target class only
        targets = torch.tensor(dataset.targets)
        target_indices = (targets == target_class).nonzero(as_tuple=True)[0]
        
        # Take a small sample (e.g., 50 images)
        sample_indices = target_indices[:50]
        subset = Subset(dataset, sample_indices)
        loader = DataLoader(subset, batch_size=25)
        
        # 3. Measure Confidence
        confidences = []
        with torch.no_grad():
            for images, _ in loader:
                images = images.to(device)
                outputs = model(images)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                
                # Get probability specifically for the target class
                target_probs = probs[:, target_class]
                confidences.extend(target_probs.cpu().tolist())
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        log.info(f"📊 Average Confidence on Class {target_class}: {avg_confidence:.4f}")
        
        return {
            "confidence": avg_confidence,
            "is_erased": avg_confidence < threshold,
            "threshold": threshold
        }

    except Exception as e:
        log.error(f"❌ Verification Failed: {e}")
        return {"confidence": 1.0, "is_erased": False, "error": str(e)}
