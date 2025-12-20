# Machine Learning Training Guide

## Overview

This guide explains how to train custom ML models for the AI Business Assistant using Jupyter notebooks and Python scripts.

## Quick Start

### 1. Install Dependencies

```bash
pip install jupyter notebook ipykernel
pip install scikit-learn transformers torch pandas numpy matplotlib seaborn
```

### 2. Create Jupyter Kernel

```bash
python -m ipykernel install --user --name=tastar-ml --display-name "Tastar ML"
```

### 3. Start Jupyter

```bash
jupyter notebook
```

Navigate to `ml/notebooks/` and open `01_document_classification.ipynb`

## Training Workflow

### Step 1: Prepare Training Data

```bash
# Extract data from database
python ml/scripts/prepare_data.py --type document_classification --output ml/data/processed/documents.csv
```

### Step 2: Train Model

**Option A: Using Jupyter Notebook (Recommended for experimentation)**
1. Open `ml/notebooks/01_document_classification.ipynb`
2. Run all cells
3. Compare models (Random Forest vs DistilBERT)
4. Save best model

**Option B: Using Training Script (Recommended for production)**
```bash
python ml/scripts/train_document_classifier.py --data ml/data/processed/documents.csv --output ml/models/document_classifier
```

### Step 3: Test Model

The trained model will automatically be used by the application when available.

## Available Models

### 1. Document Classification
- **Purpose:** Classify documents (invoice, PO, receipt, etc.)
- **Notebook:** `01_document_classification.ipynb`
- **Script:** `train_document_classifier.py`
- **Model Location:** `ml/models/document_classifier/`

### 2. Sentiment Analysis (Coming Soon)
- **Purpose:** Analyze sentiment in customer communications
- **Notebook:** `02_sentiment_analysis.ipynb`
- **Model Location:** `ml/models/sentiment_analyzer/`

### 3. Entity Extraction (Coming Soon)
- **Purpose:** Extract entities (invoice numbers, amounts, dates)
- **Notebook:** `03_entity_extraction.ipynb`
- **Model Location:** `ml/models/entity_extractor/`

### 4. Invoice Data Extraction (Coming Soon)
- **Purpose:** Extract structured data from invoices
- **Notebook:** `04_invoice_data_extraction.ipynb`
- **Model Location:** `ml/models/invoice_extractor/`

### 5. Demand Forecasting (Coming Soon)
- **Purpose:** Predict material demand
- **Notebook:** `05_demand_forecasting.ipynb`
- **Model Location:** `ml/models/demand_forecaster/`

## Model Integration

Trained models are automatically loaded by `MLService`:

```python
from app.services.ml_service import ml_service

# Classify document
result = ml_service.classify_document(text)
# Returns: {'type': 'invoice', 'confidence': 0.95, 'method': 'ml_model'}

# Analyze sentiment
result = ml_service.analyze_sentiment(text)
# Returns: {'sentiment': 'positive', 'score': 0.85, 'method': 'ml_model'}
```

## Data Collection

### From Database

The `prepare_data.py` script extracts training data from:
- `Document` table (OCR processed documents)
- `Invoice` table
- `PurchaseOrder` table
- `Quotation` table
- `Bill` table

### Manual Labeling

For better accuracy, manually label documents:
1. Upload documents via API
2. Review OCR results
3. Correct document types
4. Export labeled data using `prepare_data.py`

## Model Evaluation

Each notebook includes:
- **Train/Test Split:** 80/20 by default
- **Metrics:** Accuracy, Precision, Recall, F1-Score
- **Confusion Matrix:** Visual performance analysis
- **Model Comparison:** Compare different approaches

## Best Practices

1. **Start Small:** Begin with document classification (easiest to get data)
2. **Iterate:** Train, evaluate, improve, repeat
3. **Version Control:** Track model versions and performance
4. **Monitor:** Track model performance in production
5. **Retrain:** Periodically retrain with new data

## Troubleshooting

### "No training data found"
- Run `prepare_data.py` to extract data from database
- Or manually create CSV with 'text' and 'label' columns

### "Model not found"
- Train model first using notebook or script
- Check model is saved to `ml/models/` directory

### "Low accuracy"
- Collect more training data
- Try different model architectures
- Improve data quality (better OCR, more labels)

## Next Steps

1. ✅ Document Classification - Ready to train
2. ⏳ Sentiment Analysis - Notebook template ready
3. ⏳ Entity Extraction - Coming soon
4. ⏳ Invoice Extraction - Coming soon
5. ⏳ Demand Forecasting - Coming soon

## Resources

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Jupyter Notebook Guide](https://jupyter-notebook.readthedocs.io/)

