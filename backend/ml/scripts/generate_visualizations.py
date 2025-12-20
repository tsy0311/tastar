#!/usr/bin/env python3
"""
Generate all visualization PNGs for trained models
"""
import sys
import pickle
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data' / 'raw'

def generate_document_classifier_viz():
    """Generate visualizations for document classifier"""
    print("=" * 60)
    print("Generating Document Classifier Visualizations")
    print("=" * 60)
    
    model_dir = MODELS_DIR / 'document_classifier'
    
    try:
        # Load model
        with open(model_dir / 'model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open(model_dir / 'vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Load data for evaluation
        df = pd.read_csv(DATA_DIR / 'documents_combined.csv')
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
        )
        
        X_test_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_test_vec)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=model.classes_, yticklabels=model.classes_)
        plt.title('Document Classifier - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(model_dir / 'confusion_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ Confusion matrix saved")
        
        # Feature Importance (for RandomForest)
        if hasattr(model, 'feature_importances_'):
            feature_names = vectorizer.get_feature_names_out()
            top_indices = np.argsort(model.feature_importances_)[-30:][::-1]
            top_features = feature_names[top_indices]
            top_scores = model.feature_importances_[top_indices]
            
            plt.figure(figsize=(12, 8))
            plt.barh(range(len(top_features)), top_scores)
            plt.yticks(range(len(top_features)), top_features)
            plt.xlabel('Feature Importance')
            plt.title('Top 30 Features - Document Classifier')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(model_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✓ Feature importance saved")
        
        # Class Priors
        if hasattr(model, 'classes_'):
            class_counts = pd.Series(y_train).value_counts().reindex(model.classes_, fill_value=0)
            class_probs = class_counts / len(y_train)
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(model.classes_, class_probs, color='steelblue')
            plt.xlabel('Document Class')
            plt.ylabel('Prior Probability')
            plt.title('Class Prior Probabilities')
            plt.xticks(rotation=45)
            for bar, prob in zip(bars, class_probs):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{prob:.3f}', ha='center', va='bottom')
            plt.tight_layout()
            plt.savefig(model_dir / 'class_priors.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✓ Class priors saved")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def generate_sentiment_analyzer_viz():
    """Generate visualizations for sentiment analyzer"""
    print("\n" + "=" * 60)
    print("Generating Sentiment Analyzer Visualizations")
    print("=" * 60)
    
    model_dir = MODELS_DIR / 'sentiment_analyzer'
    
    try:
        # Load model
        with open(model_dir / 'model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open(model_dir / 'vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Load data for evaluation
        df = pd.read_csv(DATA_DIR / 'sentiment_combined.csv')
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
        )
        
        X_test_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_test_vec)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=model.classes_, yticklabels=model.classes_)
        plt.title('Sentiment Analyzer - Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(model_dir / 'nb_confusion_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ Confusion matrix saved")
        
        # Feature Importance (for Naive Bayes)
        if hasattr(model, 'feature_log_prob_'):
            feature_names = vectorizer.get_feature_names_out()
            fig, axes = plt.subplots(len(model.classes_), 1, figsize=(12, 4 * len(model.classes_)))
            if len(model.classes_) == 1:
                axes = [axes]
            
            for idx, class_name in enumerate(model.classes_):
                top_indices = np.argsort(model.feature_log_prob_[idx])[-20:][::-1]
                top_features = feature_names[top_indices]
                top_scores = model.feature_log_prob_[idx][top_indices]
                
                color = 'green' if 'positive' in str(class_name).lower() else 'red' if 'negative' in str(class_name).lower() else 'gray'
                axes[idx].barh(range(len(top_features)), top_scores, color=color)
                axes[idx].set_yticks(range(len(top_features)))
                axes[idx].set_yticklabels(top_features)
                axes[idx].set_xlabel('Log Probability')
                axes[idx].set_title(f'Top 20 Features: {class_name}')
                axes[idx].invert_yaxis()
            
            plt.tight_layout()
            plt.savefig(model_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✓ Feature importance saved")
        
        # Class Priors
        if hasattr(model, 'class_log_prior_'):
            class_probs = np.exp(model.class_log_prior_)
            plt.figure(figsize=(8, 5))
            colors = ['green' if 'positive' in str(c).lower() else 'red' if 'negative' in str(c).lower() else 'gray' 
                     for c in model.classes_]
            bars = plt.bar(model.classes_, class_probs, color=colors)
            plt.xlabel('Sentiment Class')
            plt.ylabel('Prior Probability')
            plt.title('Sentiment Class Prior Probabilities')
            for bar, prob in zip(bars, class_probs):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{prob:.3f}', ha='center', va='bottom')
            plt.tight_layout()
            plt.savefig(model_dir / 'class_priors.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✓ Class priors saved")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def generate_demand_forecaster_viz():
    """Generate visualizations for demand forecaster"""
    print("\n" + "=" * 60)
    print("Generating Demand Forecaster Visualizations")
    print("=" * 60)
    
    model_dir = MODELS_DIR / 'demand_forecaster'
    
    try:
        # Load data
        df = pd.read_csv(DATA_DIR / 'demand_forecasting_combined.csv')
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Historical data plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['demand'], marker='o', alpha=0.7, linewidth=2)
        plt.title('Demand History')
        plt.xlabel('Date')
        plt.ylabel('Demand (units)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(model_dir / 'demand_history.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ Demand history saved")
        
        # Forecast plot
        if (model_dir / 'forecast.csv').exists():
            forecast = pd.read_csv(model_dir / 'forecast.csv')
            forecast['date'] = pd.to_datetime(forecast['date'])
            
            plt.figure(figsize=(12, 6))
            plt.plot(df['date'], df['demand'], label='Historical', alpha=0.7, linewidth=2)
            plt.plot(forecast['date'], forecast['forecast'], label='Forecast', marker='o', linewidth=2)
            plt.title('Demand Forecast - Moving Average')
            plt.xlabel('Date')
            plt.ylabel('Demand (units)')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(model_dir / 'ma_forecast.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✓ Forecast visualization saved")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def generate_entity_extractor_viz():
    """Generate demo visualization for entity extractor"""
    print("\n" + "=" * 60)
    print("Generating Entity Extractor Visualization")
    print("=" * 60)
    
    model_dir = MODELS_DIR / 'entity_extractor'
    
    try:
        # Import extractor function directly
        from ml.scripts.train_entity_extractor import extract_entities_rule_based
        extractor = extract_entities_rule_based
        
        # Demo text
        demo_text = """
        Invoice #INV-2024-001
        Date: 2024-01-15
        Amount: $1,250.00
        Vendor: ABC Company
        Email: contact@abc.com
        Phone: 555-123-4567
        Tax ID: EIN-12-3456789
        """
        
        entities = extractor(demo_text)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        
        y_pos = 0.9
        ax.text(0.1, y_pos, 'Entity Extraction Demo', fontsize=16, fontweight='bold')
        y_pos -= 0.1
        
        ax.text(0.1, y_pos, 'Sample Text:', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        ax.text(0.1, y_pos, demo_text.strip(), fontsize=10, family='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        y_pos -= 0.25
        
        ax.text(0.1, y_pos, 'Extracted Entities:', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        for entity_type, values in entities.items():
            if values:
                ax.text(0.15, y_pos, f"{entity_type}: {', '.join(values)}", fontsize=10)
                y_pos -= 0.04
        
        plt.tight_layout()
        plt.savefig(model_dir / 'entity_extraction_demo.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ Entity extraction demo saved")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def generate_invoice_extractor_viz():
    """Generate demo visualization for invoice extractor"""
    print("\n" + "=" * 60)
    print("Generating Invoice Extractor Visualization")
    print("=" * 60)
    
    model_dir = MODELS_DIR / 'invoice_extractor'
    
    try:
        # Import extractor function directly
        from ml.scripts.train_invoice_extractor import extract_invoice_data
        extractor = extract_invoice_data
        
        # Demo text
        demo_text = """
        INVOICE
        Invoice Number: INV-2024-001
        Invoice Date: 2024-01-15
        Due Date: 2024-02-15
        Vendor: ABC Manufacturing
        Customer: XYZ Corp
        
        Subtotal: $1,000.00
        Tax: $100.00
        Total: $1,100.00
        
        Payment Terms: Net 30
        """
        
        extracted = extractor(demo_text)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.axis('off')
        
        y_pos = 0.95
        ax.text(0.1, y_pos, 'Invoice Data Extraction Demo', fontsize=16, fontweight='bold')
        y_pos -= 0.1
        
        ax.text(0.1, y_pos, 'Sample Invoice Text:', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        ax.text(0.1, y_pos, demo_text.strip(), fontsize=9, family='monospace',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        y_pos -= 0.3
        
        ax.text(0.1, y_pos, 'Extracted Data:', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        for key, value in extracted.items():
            if value:
                display_value = str(value) if not isinstance(value, list) else ', '.join(map(str, value))
                ax.text(0.15, y_pos, f"{key}: {display_value}", fontsize=10)
                y_pos -= 0.04
        
        plt.tight_layout()
        plt.savefig(model_dir / 'invoice_extraction_demo.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ Invoice extraction demo saved")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("Generating All Model Visualizations")
    print("=" * 60)
    
    generate_document_classifier_viz()
    generate_sentiment_analyzer_viz()
    generate_demand_forecaster_viz()
    generate_entity_extractor_viz()
    generate_invoice_extractor_viz()
    
    print("\n" + "=" * 60)
    print("✓ All visualizations generated!")
    print("=" * 60)

if __name__ == "__main__":
    main()

