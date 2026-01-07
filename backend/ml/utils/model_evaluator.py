"""
Utility functions for model evaluation
"""
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from pathlib import Path

def plot_confusion_matrix(y_true, y_pred, labels, output_path: Path = None):
    """Plot and save confusion matrix"""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Confusion matrix saved to {output_path}")
    
    plt.show()
    return cm

def evaluate_model(model, X_test, y_test, labels=None):
    """Evaluate model and return metrics"""
    y_pred = model.predict(X_test)
    
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return {
        'predictions': y_pred,
        'report': report
    }

