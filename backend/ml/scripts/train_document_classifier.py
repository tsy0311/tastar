"""
Script to train document classification model
Can be run from command line or imported as a module
"""
import argparse
import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import json

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.utils.data_loader import load_document_data
from ml.utils.model_evaluator import evaluate_model
from ml.utils.model_saver import save_model

def train_model(data_path: str = None, output_dir: str = None, test_size: float = 0.2):
    """Train document classification model"""
    
    # Set paths
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'document_classifier'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    else:
        df = load_document_data()
    
    print(f"Loaded {len(df)} training samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], 
        test_size=test_size, 
        random_state=42, 
        stratify=df['label']
    )
    
    # Vectorize
    print("\nVectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train
    print("Training Random Forest classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    save_model(model, vectorizer, output_dir, accuracy)
    
    # Save metadata
    metadata = {
        "model_type": "RandomForest",
        "accuracy": float(accuracy),
        "n_samples": len(df),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "classes": model.classes_.tolist(),
        "features": X_train_vec.shape[1]
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nModel saved to {output_dir}")
    return model, vectorizer, accuracy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train document classification model')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--output', type=str, help='Output directory for model')
    parser.add_argument('--test-size', type=float, default=0.2, help='Test set size (default: 0.2)')
    
    args = parser.parse_args()
    
    train_model(
        data_path=args.data,
        output_dir=args.output,
        test_size=args.test_size
    )

