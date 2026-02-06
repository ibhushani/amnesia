
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def unlearn_class(model, data_loader, target_class_index, optimizer, device='cuda'):
    """
    The 'Toy Code' Unlearner - Simple Gradient Ascent
    
    Args:
        model: The PyTorch model
        data_loader: DataLoader containing the data
        target_class_index: The class index to forget (e.g., 3 for Cat)
        optimizer: The optimizer
        device: 'cuda' or 'cpu'
    """
    model.train()
    print(f"Starting unlearning for class {target_class_index} on {device}...")
    
    for i, (images, labels) in enumerate(data_loader):
        images = images.to(device)
        labels = labels.to(device)
        
        # 1. Filter: Only pick the images we want to forget (e.g., Cats)
        mask = (labels == target_class_index)
        forget_images = images[mask]
        forget_labels = labels[mask]
        
        if len(forget_images) == 0:
            continue

        # 2. Forward Pass: Ask model "What is this?"
        outputs = model(forget_images)
        loss = nn.CrossEntropyLoss()(outputs, forget_labels)
        
        # 3. The "Unlearning" Magic (Gradient Ascent)
        # Normal training is: loss.backward() (Minimize error)
        # Unlearning is:      (-loss).backward() (MAXIMIZE error)
        
        optimizer.zero_grad()
        (-loss).backward() # <--- This Negative Sign is the "Unlearning"
        optimizer.step()
        
        if i % 10 == 0:
            print(f"Batch {i}: Loss {loss.item():.4f} (Maximizing this!)")
        
    print(f"Unlearning complete for class {target_class_index}")
    return model
