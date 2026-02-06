"""
Shard Aggregator - Combines predictions from multiple shards
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Literal
from models import BaseModel


class ShardAggregator:
    """
    Aggregates predictions from multiple shard models.
    
    Supports multiple aggregation strategies:
    - mean: Average logits across shards
    - vote: Majority voting on predictions
    - weighted: Weighted average based on confidence
    """
    
    def __init__(
        self,
        models: Dict[int, BaseModel],
        aggregation_method: Literal["mean", "vote", "weighted"] = "mean",
        weights: Optional[Dict[int, float]] = None,
    ):
        """
        Initialize aggregator.
        
        Args:
            models: Dictionary mapping shard index to model
            aggregation_method: How to combine predictions
            weights: Optional weights for each shard (for weighted method)
        """
        self.models = models
        self.aggregation_method = aggregation_method
        self.weights = weights
        
        if weights is None:
            # Equal weights
            self.weights = {idx: 1.0 / len(models) for idx in models.keys()}
    
    def predict(
        self,
        x: torch.Tensor,
        return_all_shards: bool = False
    ) -> torch.Tensor:
        """
        Make aggregated prediction.
        
        Args:
            x: Input tensor
            return_all_shards: If True, return predictions from all shards
            
        Returns:
            Aggregated logits or dict of all predictions
        """
        device = next(iter(self.models.values())).fc.weight.device if hasattr(
            next(iter(self.models.values())), 'fc'
        ) else next(iter(self.models.values())).classifier.weight.device
        
        x = x.to(device)
        
        # Get predictions from all shards
        shard_predictions = {}
        for shard_idx, model in self.models.items():
            model.eval()
            with torch.no_grad():
                pred = model(x)
                shard_predictions[shard_idx] = pred
        
        if return_all_shards:
            return shard_predictions
        
        # Aggregate
        if self.aggregation_method == "mean":
            return self._aggregate_mean(shard_predictions)
        elif self.aggregation_method == "vote":
            return self._aggregate_vote(shard_predictions)
        elif self.aggregation_method == "weighted":
            return self._aggregate_weighted(shard_predictions)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
    
    def _aggregate_mean(self, predictions: Dict[int, torch.Tensor]) -> torch.Tensor:
        """Average logits across shards"""
        stacked = torch.stack(list(predictions.values()))
        return stacked.mean(dim=0)
    
    def _aggregate_vote(self, predictions: Dict[int, torch.Tensor]) -> torch.Tensor:
        """Majority voting on class predictions"""
        # Get predicted classes from each shard
        votes = []
        for pred in predictions.values():
            vote = pred.argmax(dim=1)
            votes.append(vote)
        
        votes = torch.stack(votes)  # [num_shards, batch_size]
        
        # Count votes for each class
        batch_size = votes.size(1)
        num_classes = list(predictions.values())[0].size(1)
        
        # Create one-hot and sum
        result = torch.zeros(batch_size, num_classes, device=votes.device)
        for i in range(votes.size(0)):
            result.scatter_add_(1, votes[i].unsqueeze(1), 
                               torch.ones(batch_size, 1, device=votes.device))
        
        return result
    
    def _aggregate_weighted(self, predictions: Dict[int, torch.Tensor]) -> torch.Tensor:
        """Weighted average of logits"""
        result = None
        for shard_idx, pred in predictions.items():
            weight = self.weights.get(shard_idx, 1.0 / len(predictions))
            if result is None:
                result = pred * weight
            else:
                result = result + pred * weight
        return result
    
    def update_model(self, shard_idx: int, model: BaseModel):
        """Update a specific shard's model"""
        self.models[shard_idx] = model
    
    def remove_shard(self, shard_idx: int):
        """Remove a shard from aggregation"""
        if shard_idx in self.models:
            del self.models[shard_idx]
            
            # Recalculate weights
            if shard_idx in self.weights:
                del self.weights[shard_idx]
            
            # Renormalize weights
            total = sum(self.weights.values())
            if total > 0:
                self.weights = {k: v / total for k, v in self.weights.items()}
    
    def get_shard_confidences(self, x: torch.Tensor) -> Dict[int, torch.Tensor]:
        """Get confidence scores from each shard"""
        confidences = {}
        for shard_idx, model in self.models.items():
            model.eval()
            with torch.no_grad():
                logits = model(x)
                probs = F.softmax(logits, dim=1)
                confidence = probs.max(dim=1).values
                confidences[shard_idx] = confidence
        return confidences