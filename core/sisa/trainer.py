"""
SISA Trainer - Sharded training implementation
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, Subset
from typing import Dict, List, Optional, Callable, Any, Type
from pathlib import Path
import copy
from tqdm import tqdm

from utils import get_logger, generate_uuid, MetricsCollector
from models import get_model, BaseModel
from .shard_manager import ShardManager
from .aggregator import ShardAggregator

log = get_logger(__name__)


class SISATrainer:
    """
    SISA (Sharded, Isolated, Sliced, Aggregated) Trainer
    
    Implements the SISA architecture for efficient machine unlearning.
    Data is split into shards, each shard trains a separate model,
    and predictions are aggregated.
    """
    
    def __init__(
        self,
        model_class: Type[BaseModel] = None,
        model_kwargs: Dict[str, Any] = None,
        num_shards: int = 4,
        storage_path: str = "./storage/models",
        device: str = "auto",
    ):
        """
        Initialize SISA trainer.
        
        Args:
            model_class: Class of model to train (or use model_type string)
            model_kwargs: Keyword arguments for model initialization
            num_shards: Number of shards to split data into
            storage_path: Path to store trained models
            device: Device to train on ("auto", "cuda", "cpu")
        """
        self.model_class = model_class
        self.model_kwargs = model_kwargs or {}
        self.num_shards = num_shards
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Set device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Initialize components
        self.shard_manager = ShardManager(num_shards=num_shards)
        self.models: Dict[int, BaseModel] = {}
        self.aggregator: Optional[ShardAggregator] = None
        self.metrics = MetricsCollector()
        
        self._trainer_id = generate_uuid()
        
        log.info(f"Initialized SISA trainer with {num_shards} shards on {self.device}")
    
    def _create_model(self) -> BaseModel:
        """Create a new model instance"""
        if self.model_class is not None:
            return self.model_class(**self.model_kwargs)
        else:
            # Default to SimpleMLP - convert input_shape to input_dim
            from models import SimpleMLP
            kwargs = self.model_kwargs.copy()
            
            # Handle input_shape -> input_dim conversion for SimpleMLP
            if 'input_shape' in kwargs:
                input_shape = kwargs.pop('input_shape')
                # Flatten the input shape to get total dimensions
                if isinstance(input_shape, (list, tuple)):
                    import functools
                    import operator
                    kwargs['input_dim'] = functools.reduce(operator.mul, input_shape, 1)
                else:
                    kwargs['input_dim'] = input_shape
            
            # Remove 'type' key if present (from get_metadata)
            kwargs.pop('type', None)
            
            return SimpleMLP(**kwargs)
    
    def train(
        self,
        dataset: Dataset,
        data_ids: Optional[List[str]] = None,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        optimizer_class: Type[optim.Optimizer] = optim.Adam,
        criterion: nn.Module = None,
        validation_split: float = 0.1,
        callbacks: Optional[List[Callable]] = None,
    ) -> Dict[str, Any]:
        """
        Train models on sharded data.
        """
        if criterion is None:
            criterion = nn.CrossEntropyLoss()
        
        # Create shards
        log.info("Creating data shards...")
        shard_subsets = self.shard_manager.create_shards(dataset, data_ids)
        
        results = {
            "trainer_id": self._trainer_id,
            "num_shards": self.num_shards,
            "shard_results": [],
        }
        
        # Train each shard
        for shard_idx, shard_data in enumerate(shard_subsets):
            log.info(f"Training shard {shard_idx + 1}/{self.num_shards} "
                     f"({len(shard_data)} samples)")
            
            shard_result = self._train_shard(
                shard_idx=shard_idx,
                shard_data=shard_data,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
                optimizer_class=optimizer_class,
                criterion=criterion,
            )
            
            results["shard_results"].append(shard_result)
        
        # Create aggregator
        self.aggregator = ShardAggregator(
            models=self.models,
            aggregation_method="mean"
        )
        
        # Save shard manager
        self.shard_manager.save()
        
        log.info("SISA training complete!")
        return results
    
    def _train_shard(
        self,
        shard_idx: int,
        shard_data: Subset,
        epochs: int,
        batch_size: int,
        learning_rate: float,
        optimizer_class: Type[optim.Optimizer],
        criterion: nn.Module,
    ) -> Dict[str, Any]:
        """Train a single shard model"""
        # Create model for this shard
        model = self._create_model().to(self.device)
        optimizer = optimizer_class(model.parameters(), lr=learning_rate)
        
        # Create data loader
        dataloader = DataLoader(
            shard_data,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True if self.device.type == "cuda" else False,
        )
        
        # Training loop
        model.train()
        history = {"loss": [], "accuracy": []}
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            correct = 0
            total = 0
            
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                _, predicted = outputs.max(1)
                total += batch_y.size(0)
                correct += predicted.eq(batch_y).sum().item()
            
            avg_loss = epoch_loss / len(dataloader)
            accuracy = correct / total
            
            history["loss"].append(avg_loss)
            history["accuracy"].append(accuracy)
            
            if (epoch + 1) % 10 == 0:
                log.info(f"  Shard {shard_idx} Epoch {epoch + 1}/{epochs}: "
                         f"Loss={avg_loss:.4f}, Acc={accuracy:.4f}")
        
        # Save model
        model_path = self.storage_path / f"shard_{shard_idx}_{self._trainer_id}.pt"
        if hasattr(model, 'save'):
            model.save(str(model_path))
        else:
            torch.save(model.state_dict(), model_path)
        
        # Store in memory
        self.models[shard_idx] = model
        self.shard_manager.set_model_path(shard_idx, str(model_path))
        
        return {
            "shard_idx": shard_idx,
            "num_samples": len(shard_data),
            "final_loss": history["loss"][-1],
            "final_accuracy": history["accuracy"][-1],
            "model_path": str(model_path),
            "history": history,
        }
    
    def predict(
        self,
        x: torch.Tensor,
        return_all_shards: bool = False
    ) -> torch.Tensor:
        """
        Make predictions using aggregated shard models.
        """
        if self.aggregator is None:
            raise RuntimeError("Models not trained. Call train() first.")
        
        return self.aggregator.predict(x, return_all_shards)
    
    def retrain_shard(
        self,
        shard_idx: int,
        dataset: Dataset,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ) -> Dict[str, Any]:
        """
        Retrain a specific shard (used after data deletion).
        """
        # Get remaining indices for this shard
        indices = self.shard_manager.get_data_indices_for_shard(shard_idx)
        
        if len(indices) == 0:
            log.warning(f"Shard {shard_idx} has no data left!")
            return {"shard_idx": shard_idx, "status": "empty"}
        
        # Create subset with remaining data
        shard_data = Subset(dataset, indices)
        
        log.info(f"Retraining shard {shard_idx} with {len(indices)} samples")
        
        result = self._train_shard(
            shard_idx=shard_idx,
            shard_data=shard_data,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            optimizer_class=optim.Adam,
            criterion=nn.CrossEntropyLoss(),
        )
        
        # Update aggregator
        if self.aggregator is not None:
            self.aggregator.update_model(shard_idx, self.models[shard_idx])
        
        return result
    
    def get_model_for_shard(self, shard_idx: int) -> Optional[BaseModel]:
        """Get the model for a specific shard"""
        return self.models.get(shard_idx)

    def save_shard_checkpoint(self, shard_idx: int, model: nn.Module):
        """Helper for workers to save updated weights after unlearning"""
        # 1. Construct the path (consistent with _train_shard logic)
        filename = f"shard_{shard_idx}_{self._trainer_id}.pt"
        path = self.storage_path / filename
        
        # 2. Save the model weights
        if hasattr(model, 'save'):
            model.save(str(path))
        else:
            torch.save(model.state_dict(), path)

        # 3. Update the in-memory cache
        self.models[shard_idx] = model 

        # 4. Update the ShardManager registry
        self.shard_manager.set_model_path(shard_idx, str(path))
        
        log.info(f"Worker saved checkpoint for Shard {shard_idx} to {path}")
    
    def save(self, filepath: Optional[str] = None):
        """Save complete trainer state"""
        if filepath is None:
            filepath = self.storage_path / f"trainer_{self._trainer_id}.pt"
        
        state = {
            "trainer_id": self._trainer_id,
            "num_shards": self.num_shards,
            "model_kwargs": self.model_kwargs,
            "shard_model_paths": {
                idx: str(self.storage_path / f"shard_{idx}_{self._trainer_id}.pt")
                for idx in self.models.keys()
            },
        }
        
        torch.save(state, filepath)
        self.shard_manager.save()
        
        log.info(f"Saved trainer to {filepath}")
    
    def load(self, filepath: str):
        """Load trainer state"""
        state = torch.load(filepath, map_location=self.device)
        
        self._trainer_id = state["trainer_id"]
        self.num_shards = state["num_shards"]
        self.model_kwargs = state["model_kwargs"]
        
        # Load shard models
        for shard_idx, model_path in state["shard_model_paths"].items():
            model = self._create_model()
            if hasattr(model, 'load'):
                model.load(model_path)
            else:
                model.load_state_dict(torch.load(model_path, map_location=self.device))
            
            model.to(self.device)
            self.models[int(shard_idx)] = model
        
        # Recreate aggregator
        self.aggregator = ShardAggregator(self.models)
        
        log.info(f"Loaded trainer from {filepath}")