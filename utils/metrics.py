"""
Metrics collection and monitoring
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class TrainingMetrics:
    """Metrics collected during training"""
    model_id: str
    num_shards: int
    total_samples: int
    epochs: int
    final_accuracy: float
    training_time_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UnlearningMetrics:
    """Metrics collected during unlearning"""
    model_id: str
    num_samples_forgotten: int
    confidence_before: float
    confidence_after: float
    retain_accuracy_before: float
    retain_accuracy_after: float
    unlearning_time_seconds: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MetricsCollector:
    """
    Collects and stores metrics for training and unlearning operations
    """
    
    def __init__(self, storage_path: str = "./metrics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._current_operation: Optional[Dict] = None
        self._start_time: Optional[float] = None
    
    def start_operation(self, operation_type: str, metadata: Dict[str, Any]):
        """Start timing an operation"""
        self._start_time = time.time()
        self._current_operation = {
            "type": operation_type,
            "metadata": metadata,
            "started_at": datetime.now().isoformat(),
        }
    
    def end_operation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """End timing and record results"""
        if self._start_time is None:
            raise RuntimeError("No operation in progress")
        
        elapsed = time.time() - self._start_time
        
        metrics = {
            **self._current_operation,
            "results": results,
            "elapsed_seconds": elapsed,
            "ended_at": datetime.now().isoformat(),
        }
        
        # Save to file
        filename = f"{self._current_operation['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(self.storage_path / filename, "w") as f:
            json.dump(metrics, f, indent=2)
        
        self._current_operation = None
        self._start_time = None
        
        return metrics
    
    def record_training(self, metrics: TrainingMetrics):
        """Record training metrics"""
        filepath = self.storage_path / f"training_{metrics.model_id}.json"
        with open(filepath, "w") as f:
            json.dump(metrics.__dict__, f, indent=2)
    
    def record_unlearning(self, metrics: UnlearningMetrics):
        """Record unlearning metrics"""
        filepath = self.storage_path / f"unlearning_{metrics.model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, "w") as f:
            json.dump(metrics.__dict__, f, indent=2)
    
    def get_all_metrics(self) -> list:
        """Get all recorded metrics"""
        metrics = []
        for filepath in self.storage_path.glob("*.json"):
            with open(filepath) as f:
                metrics.append(json.load(f))
        return metrics