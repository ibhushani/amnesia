import pytest
import torch
import torch.nn as nn
from core.verification.membership_inference import verify_erasure
from models.mlp import SimpleMLP

def test_mia_detection():
    """Test the Membership Inference Attack logic"""
    model = SimpleMLP(input_dim=10, hidden_dims=[64, 32], num_classes=2)
    
    # Case A: Model is Confident (Erasure Failed)
    # We mock data that the model "knows" perfectly
    x_data = torch.randn(10, 10)
    y_data = torch.zeros(10).long()
    
    # Force model to overfit this data
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    for _ in range(20):
        loss = nn.CrossEntropyLoss()(model(x_data), y_data)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
    result = verify_erasure(model, x_data, y_data, threshold=0.9)
    
    # It should FAIL the erasure check because it remembers the data
    assert result['is_erased'] == False
    assert result['mean_confidence'] > 0.5

def test_mia_success():
    """Test passing the verification"""
    model = SimpleMLP(input_dim=10, hidden_dims=[64, 32], num_classes=2)
    
    # Random untrained model = Random guessing
    x_data = torch.randn(10, 10)
    y_data = torch.zeros(10).long()
    
    result = verify_erasure(model, x_data, y_data, threshold=0.9)
    
    # It should PASS because the model knows nothing (confidence ~0.5)
    assert result['is_erased'] == True