"""Directory management utilities"""
import os
from pathlib import Path


def ensure_directories():
    """Ensure all required directories exist"""
    required_dirs = [
        "data",
        "logs",
        "exports",
        "backups"
    ]
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_name}")


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent