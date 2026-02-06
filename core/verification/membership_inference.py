"""
Membership Inference Attack for verifying unlearning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from utils import get_logger

log = get_logger(__name__)


@dataclass
class MembershipResult:
    """Results from membership inference test"""
    mean_confidence: float
    max_confidence: float
    min_confidence: float
    std_confidence: float
    accuracy: float
    num_samples: int
    predicted_member: int  # How many predicted as "member" (trained on)
    

class MembershipInference:
    """
    Membership Inference Attack implementation.
    
    This "attack" tests whether specific data was used to train a model.
    - High confidence = Model likely trained on this data
    - Low confidence (near 1/num_classes) = Model likely never saw this data
    
    For unlearning verification:
    - Before unlearning: High confidence on forget set
    - After unlearning: Low confidence on forget set (success!)
    """
    
    def __init__(
        self,
        model: nn.Module,
        device: torch.device = None,
        threshold: float = 0.6,
    ):
        """
        Initialize membership inference attack.
        
        Args:
            model: Target model to attack
            device: Device to run on
            threshold: Confidence threshold for "member" classification
        """
        self.model = model
        self.device = device or torch.device("cpu")
        self.threshold = threshold
        self.model.to(self.device)
    
    def attack(
        self,
        dataloader: DataLoader,
    ) -> Dict[str, Any]:
        """
        Perform membership inference attack.
        
        Args:
            dataloader: DataLoader with data to test
            
        Returns:
            Attack results including confidence statistics
        """
        self.model.eval()
        
        all_confidences = []
        correct = 0
        total = 0
        predicted_members = 0
        
        with torch.no_grad():
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # Get model predictions
                logits = self.model(batch_x)
                probs = F.softmax(logits, dim=1)
                
                # Get confidence for correct class
                correct_probs = probs.gather(1, batch_y.view(-1, 1)).squeeze(-1)
                # Ensure it's always 1D for extending
                if correct_probs.dim() == 0:
                    correct_probs = correct_probs.unsqueeze(0)
                all_confidences.extend(correct_probs.cpu().numpy().tolist())
                
                # Calculate accuracy
                _, predicted = logits.max(1)
                correct += predicted.eq(batch_y).sum().item()
                total += batch_y.size(0)
                
                # Count predicted members (confidence > threshold)
                predicted_members += (correct_probs > self.threshold).sum().item()
        
        confidences = np.array(all_confidences)
        
        results = {
            "mean_confidence": float(np.mean(confidences)),
            "max_confidence": float(np.max(confidences)),
            "min_confidence": float(np.min(confidences)),
            "std_confidence": float(np.std(confidences)),
            "accuracy": correct / total if total > 0 else 0,
            "num_samples": total,
            "predicted_members": predicted_members,
            "membership_ratio": predicted_members / total if total > 0 else 0,
        }
        
        return results
    
    def compare_before_after(
        self,
        before_results: Dict[str, Any],
        after_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compare results before and after unlearning.
        
        Args:
            before_results: Results before unlearning
            after_results: Results after unlearning
            
        Returns:
            Comparison metrics
        """
        return {
            "confidence_drop": before_results["mean_confidence"] - after_results["mean_confidence"],
            "accuracy_drop": before_results["accuracy"] - after_results["accuracy"],
            "membership_drop": before_results["membership_ratio"] - after_results["membership_ratio"],
            "before": before_results,
            "after": after_results,
            "unlearning_effective": after_results["mean_confidence"] < self.threshold,
        }
    
    def get_per_sample_confidence(
        self,
        dataloader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get confidence for each sample individually.
        
        Returns:
            Tuple of (confidences, correct_predictions)
        """
        self.model.eval()
        
        confidences = []
        correct_predictions = []
        
        with torch.no_grad():
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                logits = self.model(batch_x)
                probs = F.softmax(logits, dim=1)
                
                correct_probs = probs.gather(1, batch_y.view(-1, 1)).squeeze()
                confidences.extend(correct_probs.cpu().numpy())
                
                _, predicted = logits.max(1)
                correct_predictions.extend(predicted.eq(batch_y).cpu().numpy())
        
        return np.array(confidences), np.array(correct_predictions)


def verify_erasure(
    model: nn.Module,
    x_data: torch.Tensor,
    y_data: torch.Tensor,
    threshold: float = 0.6,
    device: str = "auto",
) -> Dict[str, Any]:
    """
    Functional interface to verify that data has been successfully unlearned.
    
    This is a simplified wrapper for quick verification checks.
    
    Args:
        model: The model to verify
        x_data: Input data to check (should be the "forgotten" data)
        y_data: Labels for the data
        threshold: Confidence threshold. Below this = successful erasure
        device: Device to run on
        
    Returns:
        Dictionary with verification results including:
        - mean_confidence: Average confidence on the data
        - is_erased: True if mean_confidence < threshold
        - accuracy: Model accuracy on this data
        - verdict: Human-readable verdict string
    """
    from torch.utils.data import TensorDataset, DataLoader
    
    # Setup device
    if device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)
    
    # Create attack
    mi = MembershipInference(model, device=device, threshold=threshold)
    
    # Create dataloader
    dataset = TensorDataset(x_data, y_data)
    dataloader = DataLoader(dataset, batch_size=32)
    
    # Run attack
    results = mi.attack(dataloader)
    
    # Determine if erasure was successful
    is_erased = results["mean_confidence"] < threshold
    
    if is_erased:
        verdict = f"✅ ERASURE VERIFIED: Model confidence ({results['mean_confidence']:.4f}) is below threshold ({threshold})"
    else:
        verdict = f"⚠️ ERASURE INCOMPLETE: Model confidence ({results['mean_confidence']:.4f}) is still above threshold ({threshold})"
    
    return {
        "mean_confidence": results["mean_confidence"],
        "max_confidence": results["max_confidence"],
        "accuracy": results["accuracy"],
        "threshold": threshold,
        "is_erased": is_erased,
        "verdict": verdict,
        "num_samples": results["num_samples"],
    }