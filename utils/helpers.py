"""
Helper utilities for Amnesia
"""

import uuid
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional


def generate_uuid() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def ensure_dir(path: str) -> Path:
    """Ensure directory exists, create if not"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    path = Path(config_path)
    if not path.exists():
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f)


def save_json(data: Dict[str, Any], filepath: str):
    """Save data to JSON file"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file"""
    path = Path(filepath)
    if not path.exists():
        return None
    
    with open(path) as f:
        return json.load(f)


def format_bytes(size: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def calculate_model_size(model) -> int:
    """Calculate model size in bytes"""
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    return param_size + buffer_size