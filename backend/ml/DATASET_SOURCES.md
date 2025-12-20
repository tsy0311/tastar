# Document Classification Dataset Sources

This guide lists public datasets you can use for training document classification models.

## Recommended Datasets

### 1. Hugging Face Datasets (Easiest)

**No authentication required!**

```python
from ml.utils.data_loader import download_huggingface_dataset

# Synthetic invoices dataset
df = download_huggingface_dataset("rcds/synthetic-invoices", limit=200)

# Or search for other document datasets:
# https://huggingface.co/datasets?search=document+classification
```

**Popular Hugging Face Datasets:**
- `rcds/synthetic-invoices` - Synthetic invoice documents
- `tner/tweetner7` - Named entity recognition (can be adapted)
- `imdb` - Movie reviews (can be adapted for business documents)

### 2. Kaggle Datasets

**Requires Kaggle API setup:**

1. **Install Kaggle API:**
   ```bash
   pip install kaggle
   ```

2. **Get API credentials:**
   - Go to https://www.kaggle.com/account
   - Create API token
   - Save `kaggle.json` to `~/.kaggle/` (or `C:\Users\YourName\.kaggle\` on Windows)

3. **Download dataset:**
   ```python
   from ml.utils.data_loader import download_kaggle_dataset
   
   # Example: Document classification dataset
   df = download_kaggle_dataset("username/dataset-name")
   ```

**Recommended Kaggle Datasets:**
- Search for "document classification" on Kaggle
- Look for invoice, receipt, or business document datasets
- Many datasets are free and publicly available

### 3. Google Drive / Public URLs

**For publicly shared datasets:**

```python
# If you have a Google Drive public link
# Use gdown to download
!pip install gdown
!gdown --id YOUR_FILE_ID

# Or use direct download in the data_loader utility
```

### 4. Create Your Own Dataset

**From your database:**

```bash
# Extract data from your database
python ml/scripts/prepare_data.py --type document_classification --output ml/data/processed/documents.csv
```

## Quick Start Examples

### Example 1: Use Hugging Face (Recommended for beginners)

```python
from ml.utils.data_loader import download_huggingface_dataset

# Download and adapt a dataset
df = download_huggingface_dataset("imdb", split="train", limit=100)

# Adapt labels for document classification
df['label'] = df['text'].apply(lambda x: 
    'invoice' if 'invoice' in x.lower() else
    'purchase_order' if 'order' in x.lower() else
    'receipt' if 'receipt' in x.lower() else
    'general'
)
```

### Example 2: Use Kaggle Dataset

```python
from ml.utils.data_loader import download_kaggle_dataset

# Download a document classification dataset
# Replace with actual dataset name from Kaggle
df = download_kaggle_dataset("username/document-classification-dataset")
```

### Example 3: Combine Multiple Sources

```python
import pandas as pd
from ml.utils.data_loader import (
    download_huggingface_dataset,
    download_kaggle_dataset,
    load_document_data
)

# Load from multiple sources
dfs = []

# From Hugging Face
hf_df = download_huggingface_dataset("rcds/synthetic-invoices", limit=100)
if hf_df is not None:
    dfs.append(hf_df)

# From local database/CSV
local_df = load_document_data()
if local_df is not None:
    dfs.append(local_df)

# Combine
if dfs:
    df = pd.concat(dfs, ignore_index=True)
    print(f"Combined dataset: {len(df)} samples")
```

## Dataset Format

Your dataset should have at least these columns:
- `text`: Document text content
- `label`: Document type (invoice, purchase_order, receipt, quotation, etc.)

Example:
```csv
text,label
"Invoice #123\nDate: 2024-01-15\nAmount: $1000",invoice
"Purchase Order PO-001\nSupplier: ABC Corp",purchase_order
```

## Tips

1. **Start Small:** Begin with 100-200 samples to test your pipeline
2. **Balance Classes:** Ensure each document type has enough samples
3. **Quality over Quantity:** Better to have 100 good samples than 1000 noisy ones
4. **Augment Data:** Use data augmentation techniques to increase dataset size
5. **Validate Labels:** Always check a sample of your data to ensure labels are correct

## Next Steps

1. Choose a dataset source
2. Download sample data
3. Inspect and clean the data
4. Train your model
5. Evaluate and iterate

For more information, see the training guide: `TRAINING_GUIDE.md`

