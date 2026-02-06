"""
Constraints for stable unlearning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class UnlearningConstraints:
    """
    Provides constraint terms to stabilize unlearning.
    
    Without constraints, gradient ascent can:
    1. Explode weights to infinity
    2. Destroy knowledge about retained data
    3. Make the model output garbage
    
    These constraints prevent that.
    """
    
    def __init__(
        self,
        model: nn.Module,
        reference_model: Optional[nn.Module] = None,
    ):
        """
        Initialize constraints.
        
        Args:
            model: The model being unlearned
            reference_model: Optional reference model (original state)
        """
        self.model = model
        self.reference_model = reference_model
        
        # Store original parameters if no reference provided
        if reference_model is None:
            self.original_params = {
                name: param.data.clone()
                for name, param in model.named_parameters()
            }
        else:
            self.original_params = {
                name: param.data.clone()
                for name, param in reference_model.named_parameters()
            }
    
    def weight_distance_penalty(self, weight: float = 1.0) -> torch.Tensor:
        """
        Penalize deviation from original weights.
        
        L2 distance: ||θ - θ_original||²
        
        This prevents weights from drifting too far during unlearning.
        """
        penalty = 0.0
        for name, param in self.model.named_parameters():
            if name in self.original_params:
                diff = param - self.original_params[name].to(param.device)
                penalty = penalty + (diff ** 2).sum()
        
        return weight * penalty
    
    def elastic_weight_consolidation(
        self,
        fisher_diagonal: Dict[str, torch.Tensor],
        weight: float = 1.0
    ) -> torch.Tensor:
        """
        Elastic Weight Consolidation (EWC) penalty.
        
        EWC = Σ F_i × (θ_i - θ_original_i)²
        
        Penalizes changes to important weights (high Fisher) more than
        unimportant weights (low Fisher).
        """
        penalty = 0.0
        for name, param in self.model.named_parameters():
            if name in self.original_params and name in fisher_diagonal:
                diff = param - self.original_params[name].to(param.device)
                fisher = fisher_diagonal[name].to(param.device)
                penalty = penalty + (fisher * (diff ** 2)).sum()
        
        return weight * penalty
    
    def output_preservation_loss(
        self,
        x_retain: torch.Tensor,
        original_outputs: torch.Tensor,
        temperature: float = 2.0,
    ) -> torch.Tensor:
        """
        Knowledge distillation loss to preserve outputs on retained data.
        
        KL(softmax(current/T) || softmax(original/T))
        
        This ensures the model behaves similarly on retained data.
        """
        current_outputs = self.model(x_retain)
        
        # Soft targets with temperature
        soft_targets = F.softmax(original_outputs / temperature, dim=1)
        soft_current = F.log_softmax(current_outputs / temperature, dim=1)
        
        loss = F.kl_div(soft_current, soft_targets, reduction='batchmean')
        
        return loss * (temperature ** 2)
    
    def gradient_clipping_norm(self, max_norm: float = 1.0):
        """
        Clip gradients to prevent explosion during unlearning.
        
        Call this after loss.backward() and before optimizer.step()
        """
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm)
    
    def weight_magnitude_penalty(self, weight: float = 0.01) -> torch.Tensor:
        """
        L2 regularization on weight magnitudes.
        
        Prevents weights from exploding during gradient ascent.
        """
        penalty = 0.0
        for param in self.model.parameters():
            penalty = penalty + (param ** 2).sum()
        
        return weight * penalty