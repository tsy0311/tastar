# Machine Learning Training Infrastructure

This directory contains Jupyter notebooks and training scripts for training custom ML models for the AI Business Assistant.

## Structure

```
ml/
├── notebooks/              # Jupyter notebooks for training
│   ├── 01_document_classification.ipynb
│   ├── 02_sentiment_analysis.ipynb
│   ├── 03_entity_extraction.ipynb
│   ├── 04_invoice_data_extraction.ipynb
│   └── 05_demand_forecasting.ipynb
├── models/                 # Trained model files
│   ├── document_classifier/
│   ├── sentiment_analyzer/
│   └── entity_extractor/
├── data/                   # Training data
│   ├── raw/               # Raw data files
│   ├── processed/         # Processed/prepared data
│   └── samples/           # Sample documents for training
├── scripts/               # Python training scripts
│   ├── train_document_classifier.py
│   ├── train_sentiment_analyzer.py
│   └── prepare_data.py
└── utils/                 # Utility functions
    ├── data_loader.py
    ├── model_evaluator.py
    └── model_saver.py
```

## Setup

1. **Install Jupyter and ML dependencies:**
   ```bash
   pip install jupyter notebook ipykernel
   pip install scikit-learn transformers torch pandas numpy matplotlib seaborn
   ```

2. **Create Jupyter kernel:**
   ```bash
   python -m ipykernel install --user --name=tastar-ml --display-name "Tastar ML"
   ```

3. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

## Training Models

### 1. Document Classification
- **Notebook:** `notebooks/01_document_classification.ipynb`
- **Purpose:** Classify documents (invoice, PO, receipt, etc.)
- **Model Type:** Transformer-based (DistilBERT) or Traditional ML (Random Forest)
- **Training Data:** Labeled documents from OCR processing

### 2. Sentiment Analysis
- **Notebook:** `notebooks/02_sentiment_analysis.ipynb`
- **Purpose:** Analyze sentiment in customer communications
- **Model Type:** Fine-tuned BERT or DistilBERT
- **Training Data:** Customer emails, reviews, feedback

### 3. Entity Extraction (NER)
- **Notebook:** `notebooks/03_entity_extraction.ipynb`
- **Purpose:** Extract entities (invoice numbers, amounts, dates, etc.)
- **Model Type:** Named Entity Recognition (spaCy or Transformers)
- **Training Data:** Annotated documents

### 4. Invoice Data Extraction
- **Notebook:** `notebooks/04_invoice_data_extraction.ipynb`
- **Purpose:** Extract structured data from invoices
- **Model Type:** Custom NER or LayoutLM
- **Training Data:** Labeled invoice fields

### 5. Demand Forecasting
- **Notebook:** `notebooks/05_demand_forecasting.ipynb`
- **Purpose:** Predict material demand
- **Model Type:** Time series (ARIMA, LSTM, Prophet)
- **Training Data:** Historical order data

## Using Trained Models

After training, models are saved to `ml/models/` and can be loaded in the application:

```python
from app.services.ml_service import MLService

ml_service = MLService()
classification = ml_service.classify_document(text)
sentiment = ml_service.analyze_sentiment(text)
entities = ml_service.extract_entities(text)
```

## Model Evaluation

Each notebook includes:
- Training/validation split
- Model evaluation metrics
- Confusion matrices
- Performance plots
- Model comparison

## Data Preparation

Use `scripts/prepare_data.py` to prepare training data from your database:

```bash
python scripts/prepare_data.py --type document_classification --output data/processed/documents.csv
```

## Best Practices

1. **Version Control:** Use DVC (Data Version Control) for large datasets
2. **Experiment Tracking:** Use MLflow or Weights & Biases
3. **Model Registry:** Store model versions and metadata
4. **A/B Testing:** Test new models against production models
5. **Monitoring:** Track model performance in production

## Next Steps

1. Collect and label training data
2. Start with document classification (easiest to get data)
3. Iterate and improve models
4. Deploy models to production
5. Monitor and retrain periodically

