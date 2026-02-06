import pytest
import torch
import torch.nn as nn
from core.unlearning.gradient_ascent import constrained_unlearning
from models.mlp import SimpleMLP

def test_unlearning_efficacy():
    """
    Crucial Test: Does unlearning actually lower confidence on the target?
    """
    torch.manual_seed(42)
    
    # 1. Setup a "Smart" Model
    model = SimpleMLP(input_dim=10, hidden_dims=[64, 32], num_classes=2)
    # Fake training: Set weights to be deterministic so it output high confidence
    with torch.no_grad():
        model.classifier.weight.fill_(0.5) 
    
    # 2. Define Victim Data
    x_forget = torch.ones(5, 10) # 5 samples
    x_retain = torch.randn(20, 10)
    y_retain = torch.randint(0, 2, (20,))
    
    # Check Initial Confidence
    model.eval()
    initial_conf = torch.softmax(model(x_forget), dim=1).max().item()
    
    # 3. Run Unlearning
    model = constrained_unlearning(
        model, 
        x_forget, x_retain, y_retain, 
        alpha=5.0, # High learning rate for test speed
        epochs=5
    )
    
    # 4. Check Final Confidence
    final_conf = torch.softmax(model(x_forget), dim=1).max().item()
    
    print(f"\nInitial Conf: {initial_conf:.4f} -> Final Conf: {final_conf:.4f}")
    
    # The confidence should have dropped
    assert final_conf < initial_conf