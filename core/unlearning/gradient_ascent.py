"""
Gradient Ascent Unlearning Engine - The core unlearning algorithm
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, Subset
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import copy

from utils import get_logger, MetricsCollector
from models import BaseModel
from .fisher import FisherComputer
from .constraints import UnlearningConstraints

log = get_logger(__name__)


@dataclass
class UnlearningConfig:
    """Configuration for unlearning process"""
    alpha: float = 10.0          # Weight for forget loss
    beta: float = 0.1            # Weight for retain loss
    gamma: float = 0.01          # Weight for Fisher regularization
    learning_rate: float = 0.01
    epochs: int = 100
    batch_size: int = 32
    gradient_clip: float = 1.0
    use_fisher: bool = True
    verification_threshold: float = 0.6


class UnlearningEngine:
    """
    Core unlearning engine implementing constrained gradient ascent.
    
    This is the heart of the system - it removes specific data from
    a trained model while preserving performance on retained data.
    
    Algorithm:
    1. Compute Fisher Information on retain set (identify important weights)
    2. For each epoch:
       a. Compute forget loss (push toward uniform distribution)
       b. Compute retain loss (maintain accuracy on kept data)
       c. Compute Fisher regularization (protect important weights)
       d. Combined loss = α×forget + β×retain + γ×fisher
       e. Update weights
    3. Verify unlearning via membership inference
    """
    
    def __init__(
        self,
        model: BaseModel,
        config: UnlearningConfig = None,
        device: str = "auto",
    ):
        """
        Initialize unlearning engine.
        
        Args:
            model: The model to unlearn from
            config: Unlearning configuration
            device: Device to run on
        """
        self.original_model = copy.deepcopy(model)
        self.model = model
        self.config = config or UnlearningConfig()
        
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        self.model.to(self.device)
        self.original_model.to(self.device)
        
        self.fisher_computer = FisherComputer(self.original_model, self.device)
        self.constraints = UnlearningConstraints(self.model, self.original_model)
        self.metrics = MetricsCollector()
        
        self.fisher_diagonal: Optional[Dict[str, torch.Tensor]] = None
    
    def unlearn(
        self,
        forget_data: Dataset,
        retain_data: Dataset,
        forget_labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """
        Perform unlearning to remove forget_data from the model.
        
        Args:
            forget_data: Data to forget (Dataset or tuple of (X, Y))
            retain_data: Data to retain (Dataset)
            forget_labels: Labels for forget data (if not in Dataset)
            
        Returns:
            Unlearning results and metrics
        """
        log.info("Starting unlearning process...")
        log.info(f"Config: α={self.config.alpha}, β={self.config.beta}, "
                f"γ={self.config.gamma}, epochs={self.config.epochs}")
        
        # Step 1: Compute Fisher Information on retain set
        if self.config.use_fisher:
            log.info("Computing Fisher Information on retain set...")
            self.fisher_diagonal = self.fisher_computer.compute(
                retain_data,
                batch_size=self.config.batch_size,
            )
        
        # Step 2: Prepare data loaders
        forget_loader = DataLoader(
            forget_data,
            batch_size=self.config.batch_size,
            shuffle=True,
        )
        retain_loader = DataLoader(
            retain_data,
            batch_size=self.config.batch_size,
            shuffle=True,
        )
        
        # Step 3: Setup optimizer
        optimizer = optim.SGD(
            self.model.parameters(),
            lr=self.config.learning_rate,
            momentum=0.9,
        )
        
        criterion = nn.CrossEntropyLoss()
        
        # Step 4: Get number of classes for uniform distribution
        sample_x, sample_y = next(iter(forget_loader))
        num_classes = self.model(sample_x.to(self.device)).size(1)
        
        # Step 5: Training loop
        history = {
            "forget_loss": [],
            "retain_loss": [],
            "fisher_loss": [],
            "total_loss": [],
        }
        
        log.info("Beginning unlearning epochs...")
        
        for epoch in range(self.config.epochs):
            epoch_forget_loss = 0.0
            epoch_retain_loss = 0.0
            epoch_fisher_loss = 0.0
            num_batches = 0
            
            self.model.train()
            
            # Create iterators
            forget_iter = iter(forget_loader)
            retain_iter = iter(retain_loader)
            
            while True:
                try:
                    forget_x, forget_y = next(forget_iter)
                except StopIteration:
                    break
                
                try:
                    retain_x, retain_y = next(retain_iter)
                except StopIteration:
                    retain_iter = iter(retain_loader)
                    retain_x, retain_y = next(retain_iter)
                
                forget_x = forget_x.to(self.device)
                forget_y = forget_y.to(self.device)
                retain_x = retain_x.to(self.device)
                retain_y = retain_y.to(self.device)
                
                optimizer.zero_grad()
                
                # ══════════════════════════════════════════════
                # LOSS A: Forget Loss (Push toward uncertainty)
                # ══════════════════════════════════════════════
                forget_logits = self.model(forget_x)
                forget_log_probs = F.log_softmax(forget_logits, dim=1)
                
                # Target: Uniform distribution [1/C, 1/C, ..., 1/C]
                uniform_dist = torch.full(
                    (forget_x.size(0), num_classes),
                    1.0 / num_classes,
                    device=self.device
                )
                
                # KL divergence to uniform = maximize entropy
                loss_forget = F.kl_div(
                    forget_log_probs,
                    uniform_dist,
                    reduction='batchmean'
                )
                
                # ══════════════════════════════════════════════
                # LOSS B: Retain Loss (Maintain accuracy)
                # ══════════════════════════════════════════════
                retain_logits = self.model(retain_x)
                loss_retain = criterion(retain_logits, retain_y)
                
                # ══════════════════════════════════════════════
                # LOSS C: Fisher Regularization (Protect important weights)
                # ══════════════════════════════════════════════
                if self.config.use_fisher and self.fisher_diagonal is not None:
                    loss_fisher = self.constraints.elastic_weight_consolidation(
                        self.fisher_diagonal,
                        weight=1.0
                    )
                else:
                    loss_fisher = torch.tensor(0.0, device=self.device)
                
                # ══════════════════════════════════════════════
                # COMBINED LOSS
                # ══════════════════════════════════════════════
                total_loss = (
                    self.config.alpha * loss_forget +
                    self.config.beta * loss_retain +
                    self.config.gamma * loss_fisher
                )
                
                # Backward pass
                total_loss.backward()
                
                # Clip gradients
                self.constraints.gradient_clipping_norm(self.config.gradient_clip)
                
                # Update weights
                optimizer.step()
                
                # Accumulate metrics
                epoch_forget_loss += loss_forget.item()
                epoch_retain_loss += loss_retain.item()
                epoch_fisher_loss += loss_fisher.item()
                num_batches += 1
            
            # Log progress
            avg_forget = epoch_forget_loss / num_batches
            avg_retain = epoch_retain_loss / num_batches
            avg_fisher = epoch_fisher_loss / num_batches
            
            history["forget_loss"].append(avg_forget)
            history["retain_loss"].append(avg_retain)
            history["fisher_loss"].append(avg_fisher)
            history["total_loss"].append(
                self.config.alpha * avg_forget +
                self.config.beta * avg_retain +
                self.config.gamma * avg_fisher
            )
            
            if (epoch + 1) % 10 == 0 or epoch == 0:
                log.info(
                    f"Epoch {epoch + 1}/{self.config.epochs} | "
                    f"Forget: {avg_forget:.4f} | "
                    f"Retain: {avg_retain:.4f} | "
                    f"Fisher: {avg_fisher:.4f}"
                )
        
        log.info("Unlearning complete!")
        
        # Step 6: Verify unlearning
        verification = self._verify_unlearning(forget_data, retain_data)
        
        return {
            "history": history,
            "verification": verification,
            "config": self.config.__dict__,
        }
    
    def _verify_unlearning(
        self,
        forget_data: Dataset,
        retain_data: Dataset,
    ) -> Dict[str, Any]:
        """Verify that unlearning was successful"""
        from core.verification import MembershipInference
        
        mi = MembershipInference(self.model, self.device)
        
        # Test on forget set
        forget_loader = DataLoader(forget_data, batch_size=self.config.batch_size)
        forget_results = mi.attack(forget_loader)
        
        # Test on retain set
        retain_loader = DataLoader(retain_data, batch_size=self.config.batch_size)
        retain_results = mi.attack(retain_loader)
        
        verification = {
            "forget_confidence": forget_results["mean_confidence"],
            "forget_accuracy": forget_results["accuracy"],
            "retain_confidence": retain_results["mean_confidence"],
            "retain_accuracy": retain_results["accuracy"],
            "success": (
                forget_results["mean_confidence"] < self.config.verification_threshold
                and retain_results["accuracy"] > 0.85
            ),
        }
        
        log.info(f"Verification Results:")
        log.info(f"  Forget Confidence: {verification['forget_confidence']:.4f} "
                f"(target: <{self.config.verification_threshold})")
        log.info(f"  Retain Accuracy: {verification['retain_accuracy']:.4f} "
                f"(target: >0.85)")
        log.info(f"  Success: {verification['success']}")
        
        return verification
    
    def unlearn_simple(
        self,
        x_forget: torch.Tensor,
        y_forget: torch.Tensor,
        x_retain: torch.Tensor,
        y_retain: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Simplified unlearning interface with raw tensors.
        
        Useful for quick testing and integration.
        """
        from torch.utils.data import TensorDataset
        
        forget_dataset = TensorDataset(x_forget, y_forget)
        retain_dataset = TensorDataset(x_retain, y_retain)
        
        return self.unlearn(forget_dataset, retain_dataset)


def constrained_unlearning(
    model: nn.Module,
    x_forget: torch.Tensor,
    x_retain: torch.Tensor,
    y_retain: torch.Tensor,
    alpha: float = 10.0,
    beta: float = 0.1,
    gamma: float = 0.01,
    epochs: int = 100,
    learning_rate: float = 0.01,
) -> nn.Module:
    """
    Functional interface for constrained unlearning.
    
    This is a simplified wrapper around UnlearningEngine for quick usage.
    
    Args:
        model: The trained model to unlearn from
        x_forget: Input tensors to forget
        x_retain: Input tensors to retain
        y_retain: Labels for retain data
        alpha: Weight for forget loss (higher = more aggressive forgetting)
        beta: Weight for retain loss (higher = better preservation)
        gamma: Weight for Fisher regularization
        epochs: Number of unlearning epochs
        learning_rate: Learning rate for gradient ascent
        
    Returns:
        The model with target data unlearned
    """
    from torch.utils.data import TensorDataset
    
    # Create config
    config = UnlearningConfig(
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        epochs=epochs,
        learning_rate=learning_rate,
    )
    
    # Create dummy y_forget (not used in KL divergence loss, but needed for Dataset)
    y_forget = torch.zeros(x_forget.size(0), dtype=torch.long)
    
    # Create datasets
    forget_dataset = TensorDataset(x_forget, y_forget)
    retain_dataset = TensorDataset(x_retain, y_retain)
    
    # Run unlearning
    engine = UnlearningEngine(model, config)
    engine.unlearn(forget_dataset, retain_dataset)
    
    return engine.model