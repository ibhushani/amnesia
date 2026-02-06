"""
Benchmark Script - Measures Unlearning Speedup vs Full Retraining
"""

import time
import torch
import pandas as pd
from pathlib import Path
from loguru import logger
import argparse

# Adjust path to include root directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sisa.trainer import SISATrainer
from data.dataset_manager import DatasetManager
from utils.metrics import Timer

def run_benchmark(dataset_name="mnist", num_shards=4, samples=1000):
    logger.info(f"🚀 Starting Benchmark on {dataset_name} with {num_shards} shards...")
    
    # 1. Setup
    dm = DatasetManager()
    dataset = dm.get_dataset(dataset_name, train=True, download=True)
    
    # Slice dataset for speed if needed
    if samples and samples < len(dataset):
        indices = torch.randperm(len(dataset))[:samples]
        dataset = torch.utils.data.Subset(dataset, indices)
    
    trainer = SISATrainer(
        model_kwargs=dm.get_metadata(dataset_name),
        num_shards=num_shards,
        storage_path="./storage/benchmark_models",
        device="auto"
    )

    # 2. Baseline: Initial Training Time
    logger.info("Phase 1: Initial Training (The 'Baked Cake')...")
    with Timer() as t_train:
        trainer.train(dataset, epochs=2) # Low epochs for speed
    train_time = t_train.duration
    logger.success(f"Initial Training Time: {train_time:.2f}s")

    # 3. The Scenario: Forget 10 random data points
    # These points will likely fall into different shards, or the same one.
    # For a fair test, we pick indices that definitely map to Shard 0.
    target_shard = 0
    shard_indices = trainer.shard_manager.get_data_indices_for_shard(target_shard)
    forget_indices = shard_indices[:10] # Forget first 10 items in Shard 0
    
    logger.info(f"Phase 2: Unlearning {len(forget_indices)} items from Shard {target_shard}...")

    # 4. Method A: Full Retraining (The Competitor)
    # In a monolithic model, we'd have to retrain on (Total - 10) samples.
    # We simulate this cost by training a generic model on the full dataset size.
    # (Approximation for comparison)
    estimated_full_retrain_time = train_time 

    # 5. Method B: SISA Unlearning (Your Innovation)
    # We only retrain Shard 0.
    with Timer() as t_unlearn:
        # Logically remove data first
        for idx in forget_indices:
            # Note: We need the global data ID. 
            # In this simple bench, we assume index mapping handles it or we call retrain directly.
            # Here we simulate the operation:
            trainer.shard_manager.remove_data_from_shard(trainer.shard_manager.index_to_data_id[idx])
            
        # Physically retrain ONLY the affected shard
        trainer.retrain_shard(target_shard, dataset, epochs=2)
        
    sisa_time = t_unlearn.duration
    logger.success(f"SISA Unlearning Time: {sisa_time:.2f}s")

    # 6. Results
    speedup = estimated_full_retrain_time / sisa_time
    
    print("\n" + "="*40)
    print(f"📊 BENCHMARK RESULTS ({dataset_name})")
    print("="*40)
    print(f"Full Retraining Time:  {estimated_full_retrain_time:.2f}s")
    print(f"Amnesia (SISA) Time:   {sisa_time:.2f}s")
    print(f"⚡ SPEEDUP FACTOR:      {speedup:.1f}x FASTER")
    print("="*40 + "\n")

    # Save metrics for paper
    results = {
        "dataset": dataset_name,
        "shards": num_shards,
        "full_time": estimated_full_retrain_time,
        "sisa_time": sisa_time,
        "speedup": speedup
    }
    pd.DataFrame([results]).to_csv("storage/benchmark_results.csv", mode='a', header=not os.path.exists("storage/benchmark_results.csv"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mnist")
    parser.add_argument("--shards", type=int, default=4)
    args = parser.parse_args()
    
    run_benchmark(args.dataset, args.shards)