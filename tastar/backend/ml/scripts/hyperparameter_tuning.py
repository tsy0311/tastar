"""
Hyperparameter Tuning Script for ML Models
Uses GridSearchCV and RandomizedSearchCV for optimal parameter selection
"""
import argparse
import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
import json
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

def tune_document_classifier(data_path: str = None, method: str = "grid", n_iter: int = 20):
    """Tune hyperparameters for document classifier"""
    
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    elif load_document_data:
        df = load_document_data()
    else:
        raise ValueError("No data path provided")
    
    print(f"Loaded {len(df)} training samples")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )
    
    # Vectorize
    print("\nVectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Define parameter grids
    param_grids = {
        'random_forest': {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        },
        'gradient_boosting': {
            'n_estimators': [100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }
    }
    
    results = {}
    
    # Tune Random Forest
    print("\n=== Tuning Random Forest ===")
    rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)
    
    if method == "grid":
        rf_search = GridSearchCV(
            rf_base, param_grids['random_forest'],
            cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
    else:
        rf_search = RandomizedSearchCV(
            rf_base, param_grids['random_forest'],
            n_iter=n_iter, cv=5, scoring='accuracy', 
            n_jobs=-1, verbose=1, random_state=42
        )
    
    rf_search.fit(X_train_vec, y_train)
    rf_best = rf_search.best_estimator_
    rf_pred = rf_best.predict(X_test_vec)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred, average='weighted')
    
    results['random_forest'] = {
        'best_params': rf_search.best_params_,
        'best_score': float(rf_search.best_score_),
        'test_accuracy': float(rf_accuracy),
        'test_f1': float(rf_f1)
    }
    
    print(f"Best RF Accuracy: {rf_accuracy:.4f}")
    print(f"Best RF Params: {rf_search.best_params_}")
    
    # Tune Gradient Boosting
    print("\n=== Tuning Gradient Boosting ===")
    gb_base = GradientBoostingClassifier(random_state=42)
    
    if method == "grid":
        gb_search = GridSearchCV(
            gb_base, param_grids['gradient_boosting'],
            cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
    else:
        gb_search = RandomizedSearchCV(
            gb_base, param_grids['gradient_boosting'],
            n_iter=n_iter, cv=5, scoring='accuracy',
            n_jobs=-1, verbose=1, random_state=42
        )
    
    gb_search.fit(X_train_vec, y_train)
    gb_best = gb_search.best_estimator_
    gb_pred = gb_best.predict(X_test_vec)
    gb_accuracy = accuracy_score(y_test, gb_pred)
    gb_f1 = f1_score(y_test, gb_pred, average='weighted')
    
    results['gradient_boosting'] = {
        'best_params': gb_search.best_params_,
        'best_score': float(gb_search.best_score_),
        'test_accuracy': float(gb_accuracy),
        'test_f1': float(gb_f1)
    }
    
    print(f"Best GB Accuracy: {gb_accuracy:.4f}")
    print(f"Best GB Params: {gb_search.best_params_}")
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'models' / 'document_classifier'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'hyperparameter_tuning_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save best model
    best_model = rf_best if rf_accuracy >= gb_accuracy else gb_best
    best_name = 'random_forest' if rf_accuracy >= gb_accuracy else 'gradient_boosting'
    
    print(f"\n=== Best Model: {best_name} ===")
    print(f"Accuracy: {max(rf_accuracy, gb_accuracy):.4f}")
    
    with open(output_dir / 'best_tuned_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    with open(output_dir / 'vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    return results

def tune_sentiment_analyzer(data_path: str = None, method: str = "grid", n_iter: int = 20):
    """Tune hyperparameters for sentiment analyzer"""
    
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    elif load_sentiment_data:
        df = load_sentiment_data()
    else:
        raise ValueError("No data path provided")
    
    print(f"Loaded {len(df)} training samples")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )
    
    # Vectorize
    print("\nVectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Define parameter grids
    param_grids = {
        'multinomial_nb': {
            'alpha': [0.1, 0.5, 1.0, 2.0, 5.0],
            'fit_prior': [True, False]
        },
        'logistic_regression': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }
    }
    
    results = {}
    
    # Tune MultinomialNB
    print("\n=== Tuning MultinomialNB ===")
    nb_base = MultinomialNB()
    
    if method == "grid":
        nb_search = GridSearchCV(
            nb_base, param_grids['multinomial_nb'],
            cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
    else:
        nb_search = RandomizedSearchCV(
            nb_base, param_grids['multinomial_nb'],
            n_iter=n_iter, cv=5, scoring='accuracy',
            n_jobs=-1, verbose=1, random_state=42
        )
    
    nb_search.fit(X_train_vec, y_train)
    nb_best = nb_search.best_estimator_
    nb_pred = nb_best.predict(X_test_vec)
    nb_accuracy = accuracy_score(y_test, nb_pred)
    nb_f1 = f1_score(y_test, nb_pred, average='weighted')
    
    results['multinomial_nb'] = {
        'best_params': nb_search.best_params_,
        'best_score': float(nb_search.best_score_),
        'test_accuracy': float(nb_accuracy),
        'test_f1': float(nb_f1)
    }
    
    print(f"Best NB Accuracy: {nb_accuracy:.4f}")
    print(f"Best NB Params: {nb_search.best_params_}")
    
    # Tune Logistic Regression
    print("\n=== Tuning Logistic Regression ===")
    lr_base = LogisticRegression(random_state=42, max_iter=1000)
    
    if method == "grid":
        lr_search = GridSearchCV(
            lr_base, param_grids['logistic_regression'],
            cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
    else:
        lr_search = RandomizedSearchCV(
            lr_base, param_grids['logistic_regression'],
            n_iter=n_iter, cv=5, scoring='accuracy',
            n_jobs=-1, verbose=1, random_state=42
        )
    
    lr_search.fit(X_train_vec, y_train)
    lr_best = lr_search.best_estimator_
    lr_pred = lr_best.predict(X_test_vec)
    lr_accuracy = accuracy_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred, average='weighted')
    
    results['logistic_regression'] = {
        'best_params': lr_search.best_params_,
        'best_score': float(lr_search.best_score_),
        'test_accuracy': float(lr_accuracy),
        'test_f1': float(lr_f1)
    }
    
    print(f"Best LR Accuracy: {lr_accuracy:.4f}")
    print(f"Best LR Params: {lr_search.best_params_}")
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'models' / 'sentiment_analyzer'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'hyperparameter_tuning_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save best model
    best_model = nb_best if nb_accuracy >= lr_accuracy else lr_best
    best_name = 'multinomial_nb' if nb_accuracy >= lr_accuracy else 'logistic_regression'
    
    print(f"\n=== Best Model: {best_name} ===")
    print(f"Accuracy: {max(nb_accuracy, lr_accuracy):.4f}")
    
    with open(output_dir / 'best_tuned_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    with open(output_dir / 'vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hyperparameter tuning for ML models')
    parser.add_argument('--model', type=str, choices=['document', 'sentiment', 'all'], 
                       default='all', help='Model to tune')
    parser.add_argument('--data', type=str, help='Path to training data CSV')
    parser.add_argument('--method', type=str, choices=['grid', 'random'], 
                       default='random', help='Search method')
    parser.add_argument('--n-iter', type=int, default=20, 
                       help='Number of iterations for random search')
    
    args = parser.parse_args()
    
    if args.model in ['document', 'all']:
        tune_document_classifier(args.data, args.method, args.n_iter)
    
    if args.model in ['sentiment', 'all']:
        tune_sentiment_analyzer(args.data, args.method, args.n_iter)


