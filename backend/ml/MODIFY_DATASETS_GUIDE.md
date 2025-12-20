# Dataset Modification Guide

## Overview

The `modify_datasets.py` script improves downloaded datasets by:
- **Cleaning data** - Remove duplicates, normalize text, handle missing values
- **Adding features** - Extract useful features for ML models
- **Improving quality** - Normalize labels, balance classes, validate data
- **Data enrichment** - Add derived features, statistics, and indicators

## Quick Start

```bash
cd backend

# Modify all datasets
python ml/scripts/modify_datasets.py --type all

# Modify specific dataset type
python ml/scripts/modify_datasets.py --type documents
python ml/scripts/modify_datasets.py --type sentiment
python ml/scripts/modify_datasets.py --type entities
python ml/scripts/modify_datasets.py --type demand
python ml/scripts/modify_datasets.py --type invoices
```

## What Gets Improved

### 1. Document Classification Dataset

**Improvements:**
- ✅ Text cleaning and normalization
- ✅ Label standardization (invoice, purchase_order, receipt, etc.)
- ✅ Remove empty/invalid texts
- ✅ Add text features: length, word count
- ✅ Add keyword indicators: has_invoice_number, has_amount, has_date, etc.
- ✅ Remove duplicates
- ✅ Balance classes (ensure minimum samples per class)

**Output:** `ml/data/processed/documents_improved.csv`

**New Columns:**
- `text_length` - Character count
- `word_count` - Word count
- `has_invoice_number` - Binary indicator
- `has_amount` - Binary indicator
- `has_date` - Binary indicator
- `has_email` - Binary indicator
- `has_phone` - Binary indicator

### 2. Sentiment Analysis Dataset

**Improvements:**
- ✅ Text cleaning
- ✅ Sentiment label normalization (positive/negative/neutral)
- ✅ Remove empty texts
- ✅ Add text features: length, word count
- ✅ Add punctuation indicators: has_exclamation, has_question
- ✅ Add uppercase_ratio (for detecting emphasis)
- ✅ Remove duplicates

**Output:** `ml/data/processed/sentiment_improved.csv`

**New Columns:**
- `text_length` - Character count
- `word_count` - Word count
- `has_exclamation` - Binary indicator
- `has_question` - Binary indicator
- `uppercase_ratio` - Ratio of uppercase characters

### 3. Entity Extraction Dataset

**Improvements:**
- ✅ Text cleaning
- ✅ Parse entity JSON strings
- ✅ Add entity count per sample
- ✅ Add entity type indicators (has_invoice_number, has_amount, etc.)
- ✅ Remove samples with no entities
- ✅ Remove duplicates

**Output:** `ml/data/processed/entity_extraction_improved.csv`

**New Columns:**
- `entities_parsed` - Parsed entity list
- `entity_count` - Number of entities per text
- `has_<entity_type>` - Binary indicators for each entity type
- `text_length` - Character count
- `word_count` - Word count

### 4. Demand Forecasting Dataset

**Improvements:**
- ✅ Convert dates to datetime format
- ✅ Remove invalid dates
- ✅ Sort by date
- ✅ Ensure demand is numeric and non-negative
- ✅ Add time-based features: year, month, day, day_of_week, etc.
- ✅ Add lag features: demand_lag_1, demand_lag_7, demand_lag_30
- ✅ Add rolling statistics: rolling_mean_7, rolling_mean_30, rolling_std_7, rolling_std_30
- ✅ Add trend features: demand_trend

**Output:** `ml/data/processed/demand_forecasting_improved.csv`

**New Columns:**
- `year`, `month`, `day` - Date components
- `day_of_week` - 0=Monday, 6=Sunday
- `day_of_year` - Day number in year
- `week_of_year` - Week number
- `is_weekend` - Binary indicator
- `is_month_start`, `is_month_end` - Binary indicators
- `demand_lag_1`, `demand_lag_7`, `demand_lag_30` - Previous demand values
- `demand_rolling_mean_7`, `demand_rolling_mean_30` - Rolling averages
- `demand_rolling_std_7`, `demand_rolling_std_30` - Rolling standard deviations
- `demand_trend` - Change from previous period

### 5. Invoice Data Extraction Dataset

**Improvements:**
- ✅ Text cleaning
- ✅ Remove empty/invalid texts
- ✅ Parse extracted_data JSON
- ✅ Extract key fields: invoice_number, total_amount, invoice_date
- ✅ Extract missing fields from text using regex
- ✅ Add field presence indicators
- ✅ Remove duplicates
- ✅ Remove samples with no invoice number

**Output:** `ml/data/processed/invoice_extraction_improved.csv`

**New Columns:**
- `extracted_data_parsed` - Parsed extracted data dict
- `invoice_number` - Extracted invoice number
- `total_amount` - Extracted total amount
- `invoice_date` - Extracted invoice date
- `text_length` - Character count
- `word_count` - Word count
- `has_invoice_number` - Binary indicator
- `has_amount` - Binary indicator
- `has_date` - Binary indicator
- `has_email` - Binary indicator

## Usage Examples

### Example 1: Modify All Datasets

```bash
python ml/scripts/modify_datasets.py --type all
```

This will:
1. Load all datasets from `ml/data/raw/`
2. Improve each dataset
3. Save improved versions to `ml/data/processed/`

### Example 2: Modify Specific Dataset

```bash
python ml/scripts/modify_datasets.py --type demand
```

### Example 3: Custom Input/Output Directories

```bash
python ml/scripts/modify_datasets.py \
    --type all \
    --input-dir ml/data/raw \
    --output-dir ml/data/processed
```

## Before and After

### Before (Raw Dataset)
```csv
text,label
"Invoice #001\nDate: 2024-01-01\nAmount: $100",invoice
"  PO-002  ",purchase_order
```

### After (Improved Dataset)
```csv
text,label,text_length,word_count,has_invoice_number,has_amount,has_date
"Invoice #001 Date: 2024-01-01 Amount: $100",invoice,45,6,1,1,1
"PO-002",purchase_order,5,1,0,0,0
```

## Tips

1. **Always modify after downloading** - Raw datasets often need cleaning
2. **Check the output** - Review improved datasets before training
3. **Use processed data for training** - Improved datasets have better features
4. **Keep raw data** - Don't delete original datasets, keep both versions

## Troubleshooting

**"File not found"**
- Make sure you've downloaded datasets first using `download_datasets.py`
- Check that files exist in `ml/data/raw/`

**"Memory error"**
- Process datasets one at a time: `--type documents`
- Reduce dataset size before modifying

**"Empty dataset after modification"**
- Check filtering criteria (e.g., minimum text length)
- Review original data quality

## Next Steps

After modifying datasets:
1. **Inspect improved data**: `pandas.read_csv("ml/data/processed/documents_improved.csv")`
2. **Train models**: Use improved datasets for training
3. **Evaluate**: Compare model performance with raw vs improved data

