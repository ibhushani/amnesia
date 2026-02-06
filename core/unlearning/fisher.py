"""
Fisher Information computation for weight importance estimation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from typing import Dict, Optional
from tqdm import tqdm

from utils import get_logger

log = get_logger(__name__)


class FisherComputer:
    """
    Computes Fisher Information Matrix diagonal for identifying important weights.
    
    Fisher Information indicates how much each parameter contributes to the model's
    predictions. Parameters with high Fisher values are "important" and should be
    protected during unlearning.
    """
    
    def __init__(self, model: nn.Module, device: torch.device = None):
        self.model = model
        self.device = device or torch.device("cpu")
        self.fisher_diagonal: Optional[Dict[str, torch.Tensor]] = None
    
    def compute(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        num_samples: Optional[int] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Compute Fisher Information diagonal.
        
        The Fisher Information for parameter θ is:
        F(θ) = E[(∂log p(y|x,θ) / ∂θ)²]
        
        We approximate this using the squared gradients of the log-likelihood.
        
        Args:
            dataset: Dataset to compute Fisher on (should be retain set)
            batch_size: Batch size for computation
            num_samples: Optional limit on number of samples to use
            
        Returns:
            Dictionary mapping parameter names to Fisher diagonal values
        """
        self.model.eval()
        
        # Initialize Fisher diagonal
        fisher = {}
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                fisher[name] = torch.zeros_like(param)
        
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        n_samples = 0
        max_samples = num_samples or len(dataset)
        
        log.info(f"Computing Fisher Information on {max_samples} samples...")
        
        for batch_x, batch_y in tqdm(dataloader, desc="Computing Fisher"):
            if n_samples >= max_samples:
                break
            
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)
            
            # Forward pass
            self.model.zero_grad()
            outputs = self.model(batch_x)
            
            # Compute log probability of correct class
            log_probs = F.log_softmax(outputs, dim=1)
            
            # For each sample, compute gradient of log probability
            for i in range(batch_x.size(0)):
                if n_samples >= max_samples:
                    break
                
                self.model.zero_grad()
                log_probs[i, batch_y[i]].backward(retain_graph=True)
                
                # Accumulate squared gradients
                for name, param in self.model.named_parameters():
                    if param.requires_grad and param.grad is not None:
                        fisher[name] += param.grad.data.clone() ** 2
                
                n_samples += 1
        
        # Normalize by number of samples
        for name in fisher:
            fisher[name] /= n_samples
        
        self.fisher_diagonal = fisher
        log.info(f"Fisher computation complete on {n_samples} samples")
        
        return fisher
    
    def get_importance_mask(
        self,
        threshold_percentile: float = 90.0
    ) -> Dict[str, torch.Tensor]:
        """
        Get binary mask of important parameters (Fisher > threshold).
        
        Args:
            threshold_percentile: Percentile threshold for importance
            
        Returns:
            Dictionary of binary masks
        """
        if self.fisher_diagonal is None:
            raise RuntimeError("Fisher not computed. Call compute() first.")
        
        # Collect all Fisher values
        all_values = torch.cat([f.flatten() for f in self.fisher_diagonal.values()])
        threshold = torch.quantile(all_values, threshold_percentile / 100.0)
        
        masks = {}
        for name, fisher in self.fisher_diagonal.items():
            masks[name] = (fisher > threshold).float()
        
        return masks
    
    def get_regularization_weights(
        self,
        scale: float = 1.0
    ) -> Dict[str, torch.Tensor]:
        """
        Get regularization weights based on Fisher (higher Fisher = more regularization).
        
        Args:
            scale: Scaling factor for weights
            
        Returns:
            Dictionary of regularization weights
        """
        if self.fisher_diagonal is None:
            raise RuntimeError("Fisher not computed. Call compute() first.")
        
        weights = {}
        for name, fisher in self.fisher_diagonal.items():
            # Normalize to [0, 1] range
            f_min, f_max = fisher.min(), fisher.max()
            if f_max > f_min:
                normalized = (fisher - f_min) / (f_max - f_min)
            else:
                normalized = torch.zeros_like(fisher)
            weights[name] = normalized * scale
        
        return weights