"""
Demo Script - End-to-End Walkthrough of the Amnesia Pipeline
"""

import sys
import os
import torch
import random
from loguru import logger

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sisa.trainer import SISATrainer
from data.dataset_manager import DatasetManager
from core.verification.membership_inference import verify_erasure

def main():
    logger.info("🟢 AMNESIA SYSTEM DEMO STARTING")
    
    # 1. Load Data
    dm = DatasetManager()
    dataset = dm.get_dataset("mnist", train=True, download=True)
    
    # Use a tiny subset for instant demo
    indices = torch.arange(500)
    tiny_dataset = torch.utils.data.Subset(dataset, indices)
    
    # 2. Initialize System
    trainer = SISATrainer(
        model_kwargs=dm.get_metadata("mnist"),
        num_shards=2, # 2 Shards for simplicity
        storage_path="./storage/demo_models"
    )
    
    # 3. Train
    logger.info("🧠 Training Sharded Models...")
    trainer.train(tiny_dataset, epochs=1)
    
    # 4. Select a Victim (Data to Forget)
    # Let's pick a random sample from Shard 0
    target_shard = 0
    shard_data_indices = trainer.shard_manager.get_data_indices_for_shard(target_shard)
    victim_index = shard_data_indices[0] # The first item in Shard 0
    
    # Get the actual data tensor for verification
    x_victim, y_victim = tiny_dataset[victim_index]
    x_victim = x_victim.unsqueeze(0) # Add batch dim
    y_victim = torch.tensor([y_victim])
    
    # 5. Check "Before" Confidence
    logger.info("🔍 Checking Model Memory BEFORE Erasure...")
    # Get prediction from specific shard
    model = trainer.get_model_for_shard(target_shard)
    model.eval()
    with torch.no_grad():
        conf_before = torch.softmax(model(x_victim), dim=1).max().item()
    logger.info(f"Confidence on Victim Data: {conf_before:.4f}")
    
    # 6. Execute Unlearning
    logger.warning(f"⚠️  Requesting Deletion for Data Index {victim_index}...")
    
    # Logical removal
    data_id = trainer.shard_manager.index_to_data_id[victim_index]
    trainer.shard_manager.remove_data_from_shard(data_id)
    
    # Physical retraining
    trainer.retrain_shard(target_shard, tiny_dataset, epochs=1)
    
    # 7. Verification (The "Proof")
    logger.info("🛡️  Verifying Erasure...")
    new_model = trainer.get_model_for_shard(target_shard)
    
    verification = verify_erasure(new_model, x_victim, y_victim)
    
    logger.info("-" * 30)
    logger.info(f"Confidence BEFORE: {conf_before:.4f}")
    logger.info(f"Confidence AFTER:  {verification['mean_confidence']:.4f}")
    logger.info(f"Is Compliant?:     {verification['is_erased']}")
    logger.info("-" * 30)
    
    if verification['is_erased']:
        logger.success("✅ DEMO PASSED: Data successfully unlearned!")
    else:
        logger.error("❌ DEMO FAILED: Model still remembers the data.")

if __name__ == "__main__":
    main()