import pytest
import torch
from torch.utils.data import TensorDataset
from core.sisa.shard_manager import ShardManager
from core.sisa.aggregator import ShardAggregator
from models.mlp import SimpleMLP

@pytest.fixture
def mock_dataset():
    X = torch.randn(100, 10) # 100 samples, 10 features
    y = torch.randint(0, 2, (100,))
    return TensorDataset(X, y)

def test_sharding_integrity(mock_dataset):
    """Test if data is split correctly without overlap"""
    manager = ShardManager(num_shards=4, storage_path="./tests/temp_shards")
    shards = manager.create_shards(mock_dataset)
    
    assert len(shards) == 4
    
    total_samples = sum(len(s) for s in shards)
    assert total_samples == 100 # No data lost
    
    # Check for overlaps (simplified check)
    indices_shard_0 = manager.get_data_indices_for_shard(0)
    indices_shard_1 = manager.get_data_indices_for_shard(1)
    
    # Intersection should be empty
    assert set(indices_shard_0).isdisjoint(set(indices_shard_1))

def test_aggregator_logic():
    """Test if the aggregator correctly averages predictions"""
    # Create 2 mock models
    model1 = SimpleMLP(input_dim=10, hidden_dims=[64, 32], num_classes=2)
    model2 = SimpleMLP(input_dim=10, hidden_dims=[64, 32], num_classes=2)
    models = {0: model1, 1: model2}
    
    aggregator = ShardAggregator(models, aggregation_method="mean")
    
    input_data = torch.randn(5, 10)
    
    # Get prediction (returns logits, not probabilities)
    logits = aggregator.predict(input_data)
    
    # Shape check: (Batch_Size, Num_Classes)
    assert logits.shape == (5, 2)
    
    # Convert to probabilities and check sum = 1.0
    probs = torch.softmax(logits, dim=1)
    assert torch.allclose(probs.sum(dim=1), torch.ones(5), atol=1e-5)