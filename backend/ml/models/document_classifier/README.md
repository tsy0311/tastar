# Document Classifier Models

This folder will contain trained document classification models after you run `../notebooks/01_document_classification.ipynb`.

## Currently Empty?

**This is normal!** Models are generated when you:
1. Run the training notebook
2. Or run: `python ../scripts/train_document_classifier.py`

## After Training

You'll see files like:
- `model.pkl` - Trained Random Forest model
- `vectorizer.pkl` - TF-IDF vectorizer
- `metadata.json` - Model accuracy and info
- `rf_confusion_matrix.png` - Evaluation visualization

## Usage

Once models are trained, they're automatically used by the application:

```python
from app.services.ml_service import ml_service

result = ml_service.classify_document("Invoice #123...")
# Returns: {'type': 'invoice', 'confidence': 0.95}
```

