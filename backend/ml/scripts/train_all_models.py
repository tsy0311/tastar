#!/usr/bin/env python3
"""
Train all 5 ML models with the latest datasets
"""
import subprocess
import sys
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
DATA_DIR = BASE_DIR / 'data' / 'raw'

# Model training scripts and their corresponding datasets
MODELS = [
    {
        'script': 'train_document_classifier.py',
        'dataset': 'documents_combined.csv',
        'name': 'Document Classifier',
        'needs_data': True
    },
    {
        'script': 'train_sentiment_analyzer.py',
        'dataset': 'sentiment_combined.csv',
        'name': 'Sentiment Analyzer',
        'needs_data': True
    },
    {
        'script': 'train_entity_extractor.py',
        'dataset': None,  # Rule-based, doesn't need data
        'name': 'Entity Extractor',
        'needs_data': False
    },
    {
        'script': 'train_invoice_extractor.py',
        'dataset': None,  # Rule-based, doesn't need data
        'name': 'Invoice Extractor',
        'needs_data': False
    },
    {
        'script': 'train_demand_forecaster.py',
        'dataset': 'demand_forecasting_combined.csv',
        'name': 'Demand Forecaster',
        'needs_data': True
    }
]

def train_all_models():
    """Train all models sequentially"""
    print("=" * 60)
    print("Training All ML Models with Latest Datasets")
    print("=" * 60)
    
    results = []
    
    for i, model in enumerate(MODELS, 1):
        script_path = SCRIPTS_DIR / model['script']
        
        print(f"\n[{i}/{len(MODELS)}] Training {model['name']}...")
        print(f"  Script: {script_path.name}")
        
        if not script_path.exists():
            print(f"  ✗ Script not found: {script_path}")
            results.append((model['name'], False, "Script not found"))
            continue
        
        # Check dataset if needed
        if model['needs_data']:
            dataset_path = DATA_DIR / model['dataset']
            print(f"  Dataset: {dataset_path.name}")
            if not dataset_path.exists():
                print(f"  ✗ Dataset not found: {dataset_path}")
                results.append((model['name'], False, "Dataset not found"))
                continue
        
        # Run training script
        try:
            cmd = [sys.executable, str(script_path)]
            
            # Add data argument if needed
            if model['needs_data']:
                cmd.extend(['--data', str(dataset_path)])
            
            result = subprocess.run(
                cmd,
                cwd=str(BASE_DIR.parent),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per model
            )
            
            if result.returncode == 0:
                print(f"  ✓ {model['name']} trained successfully!")
                results.append((model['name'], True, "Success"))
            else:
                print(f"  ✗ {model['name']} training failed!")
                print(f"  Error: {result.stderr[:200]}")
                results.append((model['name'], False, result.stderr[:200]))
        
        except subprocess.TimeoutExpired:
            print(f"  ✗ {model['name']} training timed out!")
            results.append((model['name'], False, "Timeout"))
        except Exception as e:
            print(f"  ✗ {model['name']} training error: {str(e)}")
            results.append((model['name'], False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Training Summary")
    print("=" * 60)
    
    for name, success, message in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}: {message}")
    
    successful = sum(1 for _, success, _ in results if success)
    print(f"\n{successful}/{len(MODELS)} models trained successfully")
    
    return results

if __name__ == "__main__":
    train_all_models()

