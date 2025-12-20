# Trained Models Directory

This directory stores trained ML models after you run the training notebooks.

## Structure

```
models/
├── document_classifier/    # Document classification models
├── sentiment_analyzer/     # Sentiment analysis models
├── entity_extractor/       # Entity extraction models
├── invoice_extractor/      # Invoice data extraction models
└── demand_forecaster/      # Demand forecasting models
```

## Why Are These Folders Empty?

**These folders are empty by design!** Models are generated when you:

1. **Run the training notebooks** in `../notebooks/`
2. **Run the training scripts** in `../scripts/`

Models are **not committed to git** (they're in `.gitignore`) because:
- Model files are large (can be 100MB+)
- Models should be trained on your specific data
- Models can be regenerated anytime

## How to Generate Models

### Option 1: Using Jupyter Notebooks (Recommended)

1. Open a notebook in `../notebooks/`:
   - `01_document_classification.ipynb`
   - `02_sentiment_analysis.ipynb`
   - `03_entity_extraction.ipynb`
   - `04_invoice_data_extraction.ipynb`
   - `05_demand_forecasting.ipynb`

2. Run all cells in the notebook
3. Models will be saved to the corresponding folder here

### Option 2: Using Training Scripts

```bash
# Document classification
python ml/scripts/train_document_classifier.py

# Sentiment analysis
python ml/scripts/train_sentiment_analyzer.py

# Entity extraction
python ml/scripts/train_entity_extractor.py

# Invoice extraction
python ml/scripts/train_invoice_extractor.py

# Demand forecasting
python ml/scripts/train_demand_forecaster.py
```

## What Gets Saved

After training, each model folder will contain:

- `model.pkl` - Trained model file
- `vectorizer.pkl` - Text vectorizer (if applicable)
- `metadata.json` - Model metadata (accuracy, classes, etc.)
- `*_confusion_matrix.png` - Evaluation visualizations
- `forecast.csv` - Forecast results (for forecasting models)

## Using Trained Models

Once models are trained, they're automatically loaded by the application:

```python
from app.services.ml_service import ml_service

# Models are loaded automatically when available
result = ml_service.classify_document(text)
```

## Next Steps

1. **Train your first model**: Start with `01_document_classification.ipynb`
2. **Check this folder**: After training, you'll see model files appear
3. **Use in production**: Trained models are automatically used by the app

## Note

If you want to share trained models with your team:
- Use a model registry (MLflow, Weights & Biases)
- Or store in cloud storage (S3, Google Cloud Storage)
- Don't commit large model files to git

