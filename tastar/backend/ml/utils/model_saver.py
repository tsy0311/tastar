"""
Utility functions for saving trained models
"""
import pickle
import json
from pathlib import Path
from typing import Any, Dict

def save_model(
    model: Any,
    vectorizer: Any,
    output_dir: Path,
    accuracy: float,
    metadata: Dict = None
):
    """Save trained model and vectorizer"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    with open(output_dir / 'model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save vectorizer
    with open(output_dir / 'vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save metadata
    if metadata is None:
        metadata = {}
    
    metadata['accuracy'] = float(accuracy)
    metadata['model_file'] = 'model.pkl'
    metadata['vectorizer_file'] = 'vectorizer.pkl'
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Model saved to {output_dir}")

def load_model(model_dir: Path):
    """Load trained model and vectorizer"""
    model_dir = Path(model_dir)
    
    with open(model_dir / 'model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open(model_dir / 'vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    metadata = {}
    metadata_file = model_dir / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    return model, vectorizer, metadata

