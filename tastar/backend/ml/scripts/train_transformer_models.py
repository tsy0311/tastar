"""
Train Transformer-based Models (BERT, DistilBERT) for Document Classification and Sentiment Analysis
"""
import argparse
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, EarlyStoppingCallback
)
from datasets import Dataset
import numpy as np
from typing import Dict, Any

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from ml.utils.data_loader import load_document_data, load_sentiment_data
except ImportError:
    load_document_data = None
    load_sentiment_data = None

def train_transformer_document_classifier(
    data_path: str = None,
    model_name: str = "distilbert-base-uncased",
    output_dir: str = None,
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5
):
    """Train transformer model for document classification"""
    
    # Set paths
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'document_classifier_transformer'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    elif load_document_data:
        df = load_document_data()
    else:
        raise ValueError("No data path provided")
    
    print(f"Loaded {len(df)} training samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Encode labels
    label_map = {label: idx for idx, label in enumerate(df['label'].unique())}
    reverse_label_map = {idx: label for label, idx in label_map.items()}
    df['label_encoded'] = df['label'].map(label_map)
    
    # Split data
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['label']
    )
    
    # Load tokenizer and model
    print(f"\nLoading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label_map)
    )
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            padding='max_length',
            max_length=512
        )
    
    # Create datasets
    train_dataset = Dataset.from_pandas(train_df[['text', 'label_encoded']])
    test_dataset = Dataset.from_pandas(test_df[['text', 'label_encoded']])
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)
    
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label_encoded'])
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label_encoded'])
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir / 'checkpoints'),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir=str(output_dir / 'logs'),
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=2,
        push_to_hub=False,
    )
    
    # Metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        return {'accuracy': accuracy, 'f1': f1}
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )
    
    # Train
    print("\nTraining transformer model...")
    trainer.train()
    
    # Evaluate
    print("\nEvaluating...")
    eval_results = trainer.evaluate()
    
    # Save model
    model.save_pretrained(str(output_dir / 'model'))
    tokenizer.save_pretrained(str(output_dir / 'model'))
    
    # Save metadata
    metadata = {
        "model_type": "Transformer",
        "base_model": model_name,
        "accuracy": float(eval_results['eval_accuracy']),
        "f1": float(eval_results['eval_f1']),
        "n_samples": len(df),
        "n_train": len(train_df),
        "n_test": len(test_df),
        "label_map": label_map,
        "reverse_label_map": reverse_label_map,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nModel saved to {output_dir}")
    print(f"Accuracy: {eval_results['eval_accuracy']:.4f}")
    print(f"F1 Score: {eval_results['eval_f1']:.4f}")
    
    return model, tokenizer, eval_results

def train_transformer_sentiment_analyzer(
    data_path: str = None,
    model_name: str = "distilbert-base-uncased",
    output_dir: str = None,
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5
):
    """Train transformer model for sentiment analysis"""
    
    # Set paths
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'sentiment_analyzer_transformer'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    elif load_sentiment_data:
        df = load_sentiment_data()
    else:
        raise ValueError("No data path provided")
    
    print(f"Loaded {len(df)} training samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Encode labels
    label_map = {label: idx for idx, label in enumerate(df['label'].unique())}
    reverse_label_map = {idx: label for label, idx in label_map.items()}
    df['label_encoded'] = df['label'].map(label_map)
    
    # Split data
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['label']
    )
    
    # Load tokenizer and model
    print(f"\nLoading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label_map)
    )
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            padding='max_length',
            max_length=512
        )
    
    # Create datasets
    train_dataset = Dataset.from_pandas(train_df[['text', 'label_encoded']])
    test_dataset = Dataset.from_pandas(test_df[['text', 'label_encoded']])
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)
    
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label_encoded'])
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label_encoded'])
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir / 'checkpoints'),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir=str(output_dir / 'logs'),
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=2,
        push_to_hub=False,
    )
    
    # Metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        return {'accuracy': accuracy, 'f1': f1}
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )
    
    # Train
    print("\nTraining transformer model...")
    trainer.train()
    
    # Evaluate
    print("\nEvaluating...")
    eval_results = trainer.evaluate()
    
    # Save model
    model.save_pretrained(str(output_dir / 'model'))
    tokenizer.save_pretrained(str(output_dir / 'model'))
    
    # Save metadata
    metadata = {
        "model_type": "Transformer",
        "base_model": model_name,
        "accuracy": float(eval_results['eval_accuracy']),
        "f1": float(eval_results['eval_f1']),
        "n_samples": len(df),
        "n_train": len(train_df),
        "n_test": len(test_df),
        "label_map": label_map,
        "reverse_label_map": reverse_label_map,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nModel saved to {output_dir}")
    print(f"Accuracy: {eval_results['eval_accuracy']:.4f}")
    print(f"F1 Score: {eval_results['eval_f1']:.4f}")
    
    return model, tokenizer, eval_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train transformer models')
    parser.add_argument('--model', type=str, choices=['document', 'sentiment', 'all'], 
                       default='all', help='Model to train')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--base-model', type=str, default='distilbert-base-uncased',
                       help='Base transformer model')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-5, help='Learning rate')
    
    args = parser.parse_args()
    
    if args.model in ['document', 'all']:
        train_transformer_document_classifier(
            args.data, args.base_model, args.output,
            args.epochs, args.batch_size, args.learning_rate
        )
    
    if args.model in ['sentiment', 'all']:
        train_transformer_sentiment_analyzer(
            args.data, args.base_model, args.output,
            args.epochs, args.batch_size, args.learning_rate
        )


