import os
import torch
from torchvision import datasets, transforms
import shutil

def setup_cifar10():
    print("🚀 Setting up CIFAR-10 Dataset...")
    
    # Define paths
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"📂 Data directory: {data_dir}")
    
    # Download CIFAR-10
    print("⬇️ Downloading CIFAR-10...")
    train_data = datasets.CIFAR10(root=data_dir, train=True, download=True)
    test_data = datasets.CIFAR10(root=data_dir, train=False, download=True)
    
    print("✅ CIFAR-10 Downloaded Successfully!")
    
    # Download Pre-trained ResNet-18 (Weights only)
    print("⬇️ Downloading ResNet-18 weights...")
    try:
        # We need a model structure to save standard weights
        from torchvision.models import resnet18, ResNet18_Weights
        model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        
        # Modify for CIFAR-10 (10 classes instead of 1000)
        model.fc = torch.nn.Linear(model.fc.in_features, 10)
        
        save_path = os.path.join(models_dir, "resnet18_cifar10_base.pth")
        torch.save(model.state_dict(), save_path)
        print(f"✅ Saved base ResNet-18 model to: {save_path}")
        
    except Exception as e:
        print(f"⚠️ Could not auto-download model weights: {e}")
        print("You might need to train it first or download manually.")

if __name__ == "__main__":
    setup_cifar10()
