"""
Shard Manager - Handles data sharding and tracking
"""

import torch
from torch.utils.data import Dataset, Subset
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from datetime import datetime

from utils import generate_uuid, get_logger

log = get_logger(__name__)


@dataclass
class ShardInfo:
    """Information about a single shard"""
    shard_id: str
    shard_index: int
    num_samples: int
    data_indices: List[int]
    model_path: Optional[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


@dataclass
class DataMapping:
    """Mapping of data ID to shard"""
    data_id: str
    data_index: int
    shard_id: str
    shard_index: int


class ShardManager:
    """
    Manages data sharding for SISA training.
    
    Responsibilities:
    - Split dataset into shards
    - Track which data belongs to which shard
    - Support data lookup for unlearning
    - Persist shard information
    """
    
    def __init__(
        self,
        num_shards: int = 4,
        storage_path: str = "./storage/shards",
        random_seed: int = 42
    ):
        self.num_shards = num_shards
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.random_seed = random_seed
        
        self.shards: Dict[int, ShardInfo] = {}
        self.data_to_shard: Dict[str, DataMapping] = {}
        self.index_to_data_id: Dict[int, str] = {}
        
        self._manager_id = generate_uuid()
    
    def create_shards(
        self,
        dataset: Dataset,
        data_ids: Optional[List[str]] = None
    ) -> List[Subset]:
        """
        Split dataset into shards.
        
        Args:
            dataset: PyTorch dataset to split
            data_ids: Optional list of data IDs (uses indices if not provided)
            
        Returns:
            List of Subset objects, one per shard
        """
        n_samples = len(dataset)
        
        # Generate data IDs if not provided
        if data_ids is None:
            data_ids = [f"data_{i}" for i in range(n_samples)]
        
        if len(data_ids) != n_samples:
            raise ValueError(f"data_ids length ({len(data_ids)}) must match dataset length ({n_samples})")
        
        # Create index to ID mapping
        for idx, data_id in enumerate(data_ids):
            self.index_to_data_id[idx] = data_id
        
        # Shuffle indices for random sharding
        np.random.seed(self.random_seed)
        indices = np.random.permutation(n_samples)
        
        # Split into shards
        shard_indices = np.array_split(indices, self.num_shards)
        
        subsets = []
        for shard_idx, indices_arr in enumerate(shard_indices):
            indices_list = indices_arr.tolist()
            shard_id = generate_uuid()
            
            # Create shard info
            shard_info = ShardInfo(
                shard_id=shard_id,
                shard_index=shard_idx,
                num_samples=len(indices_list),
                data_indices=indices_list,
            )
            self.shards[shard_idx] = shard_info
            
            # Map data to shards
            for data_index in indices_list:
                data_id = self.index_to_data_id[data_index]
                mapping = DataMapping(
                    data_id=data_id,
                    data_index=data_index,
                    shard_id=shard_id,
                    shard_index=shard_idx,
                )
                self.data_to_shard[data_id] = mapping
            
            # Create subset
            subset = Subset(dataset, indices_list)
            subsets.append(subset)
            
            log.info(f"Created shard {shard_idx} with {len(indices_list)} samples")
        
        return subsets
    
    def get_shard_for_data(self, data_id: str) -> Optional[int]:
        """Get shard index for a data ID"""
        mapping = self.data_to_shard.get(data_id)
        if mapping is None:
            return None
        return mapping.shard_index
    
    def get_shards_for_data_batch(self, data_ids: List[str]) -> Dict[int, List[str]]:
        """
        Get shard assignments for multiple data IDs.
        
        Returns:
            Dict mapping shard index to list of data IDs in that shard
        """
        shard_to_data: Dict[int, List[str]] = {}
        
        for data_id in data_ids:
            shard_idx = self.get_shard_for_data(data_id)
            if shard_idx is not None:
                if shard_idx not in shard_to_data:
                    shard_to_data[shard_idx] = []
                shard_to_data[shard_idx].append(data_id)
        
        return shard_to_data
    
    def remove_data_from_shard(self, data_id: str) -> Optional[int]:
        """
        Remove data from shard tracking.
        
        Returns:
            Shard index that was affected, or None if data not found
        """
        mapping = self.data_to_shard.get(data_id)
        if mapping is None:
            return None
        
        shard_idx = mapping.shard_index
        data_index = mapping.data_index
        
        # Remove from shard's data indices
        if shard_idx in self.shards:
            shard = self.shards[shard_idx]
            if data_index in shard.data_indices:
                shard.data_indices.remove(data_index)
                shard.num_samples -= 1
                shard.updated_at = datetime.now().isoformat()
        
        # Remove from mappings
        del self.data_to_shard[data_id]
        if data_index in self.index_to_data_id:
            del self.index_to_data_id[data_index]
        
        log.info(f"Removed data {data_id} from shard {shard_idx}")
        
        return shard_idx
    
    def get_shard_info(self, shard_idx: int) -> Optional[ShardInfo]:
        """Get information about a shard"""
        return self.shards.get(shard_idx)
    
    def set_model_path(self, shard_idx: int, model_path: str):
        """Set the model path for a shard"""
        if shard_idx in self.shards:
            self.shards[shard_idx].model_path = model_path
            self.shards[shard_idx].updated_at = datetime.now().isoformat()
    
    def get_data_indices_for_shard(self, shard_idx: int) -> List[int]:
        """Get all data indices in a shard"""
        if shard_idx not in self.shards:
            return []
        return self.shards[shard_idx].data_indices.copy()
    
    def save(self, filepath: Optional[str] = None):
        """Save shard manager state"""
        if filepath is None:
            filepath = self.storage_path / f"shard_manager_{self._manager_id}.json"
        
        state = {
            "manager_id": self._manager_id,
            "num_shards": self.num_shards,
            "random_seed": self.random_seed,
            "shards": {k: asdict(v) for k, v in self.shards.items()},
            "data_to_shard": {k: asdict(v) for k, v in self.data_to_shard.items()},
            "index_to_data_id": self.index_to_data_id,
        }
        
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
        
        log.info(f"Saved shard manager to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'ShardManager':
        """Load shard manager from file"""
        with open(filepath) as f:
            state = json.load(f)
        
        manager = cls(
            num_shards=state["num_shards"],
            random_seed=state["random_seed"],
        )
        manager._manager_id = state["manager_id"]
        
        # Restore shards
        for k, v in state["shards"].items():
            manager.shards[int(k)] = ShardInfo(**v)
        
        # Restore mappings
        for k, v in state["data_to_shard"].items():
            manager.data_to_shard[k] = DataMapping(**v)
        
        manager.index_to_data_id = {int(k): v for k, v in state["index_to_data_id"].items()}
        
        log.info(f"Loaded shard manager from {filepath}")
        return manager