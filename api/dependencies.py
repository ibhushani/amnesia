"""
FastAPI Dependencies
"""
from fastapi import Depends
from api.config import Settings, get_settings
from core.sisa.trainer import SISATrainer
from core.sisa.shard_manager import ShardManager

# Singleton instances to avoid re-initializing heavy objects
_trainer_instance = None
_shard_manager_instance = None

def get_shard_manager(settings: Settings = Depends(get_settings)) -> ShardManager:
    global _shard_manager_instance
    if _shard_manager_instance is None:
        _shard_manager_instance = ShardManager(
            num_shards=4, # Default, can be overridden by config
            storage_path=settings.STORAGE_ROOT + "/shards"
        )
    return _shard_manager_instance

def get_sisa_trainer(
    settings: Settings = Depends(get_settings),
    # In a real app, you might inject the model class here
) -> SISATrainer:
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = SISATrainer(
            num_shards=4,
            storage_path=settings.MODEL_STORAGE
        )
    return _trainer_instance