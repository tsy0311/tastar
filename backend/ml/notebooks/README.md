# Jupyter Notebooks for ML Training

This directory contains Jupyter notebooks for training machine learning models.

## Why Notebooks Are Here

**Notebooks are separate from models** because:

1. **Notebooks = Training Code** (small, version-controlled)
2. **Models = Trained Artifacts** (large, generated, not in git)

This is a standard ML project structure:
- `notebooks/` - Training and experimentation code
- `models/` - Generated model files (after training)
- `scripts/` - Production training scripts
- `data/` - Training datasets

## Available Notebooks

### 1. Document Classification (`01_document_classification.ipynb`)
- **Purpose**: Classify documents (invoice, PO, receipt, etc.)
- **Output**: Model saved to `../models/document_classifier/`
- **Run time**: ~2-5 minutes

### 2. Sentiment Analysis (`02_sentiment_analysis.ipynb`)
- **Purpose**: Analyze sentiment in customer communications
- **Output**: Model saved to `../models/sentiment_analyzer/`
- **Run time**: ~1-3 minutes

### 3. Entity Extraction (`03_entity_extraction.ipynb`)
- **Purpose**: Extract entities (invoice numbers, amounts, dates, etc.)
- **Output**: Extractor saved to `../models/entity_extractor/`
- **Run time**: ~1-2 minutes (rule-based, no training needed)

### 4. Invoice Data Extraction (`04_invoice_data_extraction.ipynb`)
- **Purpose**: Extract structured data from invoices
- **Output**: Extractor saved to `../models/invoice_extractor/`
- **Run time**: ~1-2 minutes (rule-based)

### 5. Demand Forecasting (`05_demand_forecasting.ipynb`)
- **Purpose**: Predict material demand using time series
- **Output**: Forecast saved to `../models/demand_forecaster/`
- **Run time**: ~2-5 minutes

## How to Use

### Step 1: Start Jupyter

```bash
cd backend/ml
jupyter notebook
```

### Step 2: Open a Notebook

Click on any notebook (e.g., `01_document_classification.ipynb`)

### Step 3: Run Cells

1. **First cell**: Installs dependencies (`!pip install ...`)
2. **Subsequent cells**: Run in order (Shift+Enter)
3. **Last cells**: Save models to `../models/` folder

### Step 4: Check Results

After running, check `../models/` folder - you'll see:
- Model files (`.pkl`)
- Metadata (`.json`)
- Visualizations (`.png`)

## Notebook Structure

Each notebook follows this pattern:

```python
# Cell 1: Install dependencies
!pip install ...

# Cell 2: Imports and setup
import ...

# Cell 3: Load data
df = load_data()

# Cell 4: Train model
model = train_model(df)

# Cell 5: Evaluate
evaluate_model(model)

# Cell 6: Save model
save_model(model, '../models/...')
```

## Mobile/Portable Use

Each notebook's **first cell includes all dependencies**, so you can:
- Run on any machine
- No need to pre-install packages
- Works in Google Colab, JupyterHub, etc.

## Tips

1. **Run cells sequentially** - Don't skip cells
2. **Check outputs** - Make sure each cell completes successfully
3. **Save models** - Models are saved automatically in the last cell
4. **Experiment** - Modify parameters and re-run to improve accuracy

## Troubleshooting

### "Module not found"
- Run the first cell again (pip install)
- Restart kernel and run all cells

### "Model folder is empty"
- Make sure you ran all cells
- Check for errors in the notebook output
- Models are saved in the last cell

### "No data found"
- Notebooks generate sample data automatically
- Or use `prepare_data.py` to extract from database

