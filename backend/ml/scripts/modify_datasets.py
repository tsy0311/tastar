#!/usr/bin/env python3
"""
Modify and improve downloaded datasets
- Clean data
- Add features
- Improve quality
- Data augmentation
"""
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import re
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def clean_text(text):
    """Clean and normalize text"""
    if pd.isna(text):
        return ""
    
    text = str(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.,!?;:\-\(\)\$\%\@]', '', text)
    return text.strip()

def improve_documents_dataset(input_file: str, output_file: str = None):
    """Improve document classification dataset"""
    print("=" * 60)
    print("Improving Document Classification Dataset")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    print(f"Original dataset: {len(df)} samples")
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Remove empty texts
    df = df[df['text'].str.len() > 10]
    
    # Normalize labels
    label_mapping = {
        'invoice': 'invoice',
        'Invoice': 'invoice',
        'INVOICE': 'invoice',
        'purchase_order': 'purchase_order',
        'Purchase Order': 'purchase_order',
        'PO': 'purchase_order',
        'receipt': 'receipt',
        'Receipt': 'receipt',
        'quotation': 'quotation',
        'Quote': 'quotation',
        'delivery_order': 'delivery_order',
        'Delivery': 'delivery_order',
        'general': 'general',
        'General': 'general'
    }
    df['label'] = df['label'].map(label_mapping).fillna('general')
    
    # Add text length feature
    df['text_length'] = df['text'].str.len()
    
    # Add word count
    df['word_count'] = df['text'].str.split().str.len()
    
    # Add keyword features
    keywords = {
        'has_invoice_number': r'inv|invoice\s*#',
        'has_amount': r'\$[\d,]+\.?\d*',
        'has_date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        'has_email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'has_phone': r'\d{3}[-.]?\d{3}[-.]?\d{4}'
    }
    
    for feature, pattern in keywords.items():
        df[feature] = df['text'].str.contains(pattern, case=False, regex=True, na=False).astype(int)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['text'], keep='first')
    
    # Balance classes (optional - keep all but ensure minimum)
    min_samples = 10
    balanced_df = []
    for label in df['label'].unique():
        label_df = df[df['label'] == label]
        if len(label_df) < min_samples:
            # Duplicate samples to reach minimum
            while len(label_df) < min_samples:
                label_df = pd.concat([label_df, label_df], ignore_index=True)
            label_df = label_df.head(min_samples)
        balanced_df.append(label_df)
    
    df = pd.concat(balanced_df, ignore_index=True)
    
    if output_file is None:
        output_file = input_file.replace('.csv', '_improved.csv')
    
    df.to_csv(output_file, index=False)
    print(f"✓ Improved dataset saved: {output_file}")
    print(f"  Total samples: {len(df)}")
    print(f"  Label distribution:")
    print(df['label'].value_counts())
    return df

def improve_sentiment_dataset(input_file: str, output_file: str = None):
    """Improve sentiment analysis dataset"""
    print("=" * 60)
    print("Improving Sentiment Analysis Dataset")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    print(f"Original dataset: {len(df)} samples")
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Remove empty texts
    df = df[df['text'].str.len() > 5]
    
    # Normalize sentiment labels
    label_mapping = {
        'positive': 'positive',
        'Positive': 'positive',
        'POSITIVE': 'positive',
        '1': 'positive',
        1: 'positive',
        'negative': 'negative',
        'Negative': 'negative',
        'NEGATIVE': 'negative',
        '0': 'negative',
        0: 'negative',
        'neutral': 'neutral',
        'Neutral': 'neutral'
    }
    df['label'] = df['label'].map(label_mapping).fillna('neutral')
    
    # Remove neutral for binary classification (optional)
    # df = df[df['label'] != 'neutral']
    
    # Add features
    df['text_length'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    df['has_exclamation'] = df['text'].str.contains('!', na=False).astype(int)
    df['has_question'] = df['text'].str.contains('\?', na=False).astype(int)
    df['uppercase_ratio'] = df['text'].apply(lambda x: sum(c.isupper() for c in str(x)) / max(len(str(x)), 1))
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['text'], keep='first')
    
    if output_file is None:
        output_file = input_file.replace('.csv', '_improved.csv')
    
    df.to_csv(output_file, index=False)
    print(f"✓ Improved dataset saved: {output_file}")
    print(f"  Total samples: {len(df)}")
    print(f"  Label distribution:")
    print(df['label'].value_counts())
    return df

def improve_entity_extraction_dataset(input_file: str, output_file: str = None):
    """Improve entity extraction dataset"""
    print("=" * 60)
    print("Improving Entity Extraction Dataset")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    print(f"Original dataset: {len(df)} samples")
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Parse entities if stored as string
    if 'entities' in df.columns:
        def parse_entities(ent_str):
            try:
                if isinstance(ent_str, str):
                    # Try to parse as JSON or Python list
                    ent_str = ent_str.replace("'", '"')
                    return json.loads(ent_str)
                return ent_str
            except:
                return []
        
        df['entities_parsed'] = df['entities'].apply(parse_entities)
        
        # Add entity count
        df['entity_count'] = df['entities_parsed'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # Extract entity types
        entity_types = set()
        for ents in df['entities_parsed']:
            if isinstance(ents, list):
                for ent in ents:
                    if isinstance(ent, dict) and 'label' in ent:
                        entity_types.add(ent['label'])
        
        for ent_type in entity_types:
            df[f'has_{ent_type}'] = df['entities_parsed'].apply(
                lambda x: 1 if isinstance(x, list) and any(e.get('label') == ent_type for e in x if isinstance(e, dict)) else 0
            )
    
    # Add text features
    df['text_length'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    
    # Remove samples with no entities
    if 'entity_count' in df.columns:
        df = df[df['entity_count'] > 0]
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['text'], keep='first')
    
    if output_file is None:
        output_file = input_file.replace('.csv', '_improved.csv')
    
    df.to_csv(output_file, index=False)
    print(f"✓ Improved dataset saved: {output_file}")
    print(f"  Total samples: {len(df)}")
    if 'entity_count' in df.columns:
        print(f"  Average entities per sample: {df['entity_count'].mean():.2f}")
    return df

def improve_demand_forecasting_dataset(input_file: str, output_file: str = None):
    """Improve demand forecasting dataset"""
    print("=" * 60)
    print("Improving Demand Forecasting Dataset")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    print(f"Original dataset: {len(df)} samples")
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Remove invalid dates
    df = df[df['date'].notna()]
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Ensure demand is numeric and non-negative
    df['demand'] = pd.to_numeric(df['demand'], errors='coerce').fillna(0)
    df['demand'] = df['demand'].clip(lower=0)
    
    # Add time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_month_start'] = (df['day'] <= 3).astype(int)
    df['is_month_end'] = (df['day'] >= 28).astype(int)
    
    # Add lag features
    for lag in [1, 7, 30]:
        df[f'demand_lag_{lag}'] = df.groupby('material_id')['demand'].shift(lag)
    
    # Add rolling statistics
    for window in [7, 30]:
        df[f'demand_rolling_mean_{window}'] = df.groupby('material_id')['demand'].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        df[f'demand_rolling_std_{window}'] = df.groupby('material_id')['demand'].transform(
            lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
        )
    
    # Add trend features
    df['demand_trend'] = df.groupby('material_id')['demand'].transform(
        lambda x: x.diff().fillna(0)
    )
    
    # Remove rows with missing critical data
    df = df[df['demand'].notna()]
    
    if output_file is None:
        output_file = input_file.replace('.csv', '_improved.csv')
    
    df.to_csv(output_file, index=False)
    print(f"✓ Improved dataset saved: {output_file}")
    print(f"  Total samples: {len(df)}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Materials: {df['material_id'].nunique()}")
    print(f"  Average demand: {df['demand'].mean():.2f}")
    return df

def improve_invoice_extraction_dataset(input_file: str, output_file: str = None):
    """Improve invoice data extraction dataset"""
    print("=" * 60)
    print("Improving Invoice Data Extraction Dataset")
    print("=" * 60)
    
    df = pd.read_csv(input_file)
    print(f"Original dataset: {len(df)} samples")
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Remove empty texts
    df = df[df['text'].str.len() > 50]
    
    # Parse extracted_data if it's a string
    if 'extracted_data' in df.columns:
        def parse_extracted_data(data_str):
            try:
                if isinstance(data_str, str):
                    data_str = data_str.replace("'", '"')
                    return json.loads(data_str)
                return data_str
            except:
                return {}
        
        df['extracted_data_parsed'] = df['extracted_data'].apply(parse_extracted_data)
        
        # Extract key fields if not already present
        if 'invoice_number' not in df.columns:
            df['invoice_number'] = df['extracted_data_parsed'].apply(
                lambda x: x.get('invoice_number', '') if isinstance(x, dict) else ''
            )
        
        if 'total_amount' not in df.columns:
            df['total_amount'] = df['extracted_data_parsed'].apply(
                lambda x: float(x.get('total', 0) or x.get('total_amount', 0)) if isinstance(x, dict) else 0
            )
        
        if 'invoice_date' not in df.columns:
            df['invoice_date'] = df['extracted_data_parsed'].apply(
                lambda x: x.get('invoice_date', '') if isinstance(x, dict) else ''
            )
    
    # Extract fields from text if missing
    if 'invoice_number' in df.columns:
        df['invoice_number'] = df.apply(
            lambda row: row['invoice_number'] if row['invoice_number'] else 
            re.search(r'(?:invoice|inv)[\s#:]*([A-Z0-9\-]+)', str(row['text']), re.IGNORECASE).group(1) 
            if re.search(r'(?:invoice|inv)[\s#:]*([A-Z0-9\-]+)', str(row['text']), re.IGNORECASE) else '',
            axis=1
        )
    
    if 'total_amount' in df.columns:
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
        # Extract from text if missing
        df['total_amount'] = df.apply(
            lambda row: row['total_amount'] if row['total_amount'] > 0 else
            float(re.search(r'total[:\s]*\$?([\d,]+\.?\d*)', str(row['text']), re.IGNORECASE).group(1).replace(',', ''))
            if re.search(r'total[:\s]*\$?([\d,]+\.?\d*)', str(row['text']), re.IGNORECASE) else 0,
            axis=1
        )
    
    # Add text features
    df['text_length'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    
    # Add field presence indicators
    df['has_invoice_number'] = (df['invoice_number'].str.len() > 0).astype(int) if 'invoice_number' in df.columns else 0
    df['has_amount'] = (df['total_amount'] > 0).astype(int) if 'total_amount' in df.columns else 0
    df['has_date'] = df['text'].str.contains(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', regex=True, na=False).astype(int)
    df['has_email'] = df['text'].str.contains(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', regex=True, na=False).astype(int)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['text'], keep='first')
    
    # Remove samples with no extracted data
    if 'has_invoice_number' in df.columns:
        df = df[df['has_invoice_number'] == 1]
    
    if output_file is None:
        output_file = input_file.replace('.csv', '_improved.csv')
    
    df.to_csv(output_file, index=False)
    print(f"✓ Improved dataset saved: {output_file}")
    print(f"  Total samples: {len(df)}")
    if 'total_amount' in df.columns:
        print(f"  Average amount: ${df['total_amount'].mean():.2f}")
    return df

def main():
    parser = argparse.ArgumentParser(description='Modify and improve datasets')
    parser.add_argument('--type', type=str, 
                       choices=['documents', 'sentiment', 'entities', 'demand', 'invoices', 'all'],
                       default='all', help='Type of dataset to improve')
    parser.add_argument('--input-dir', type=str, 
                       default='ml/data/raw',
                       help='Input directory with datasets')
    parser.add_argument('--output-dir', type=str,
                       default='ml/data/processed',
                       help='Output directory for improved datasets')
    
    args = parser.parse_args()
    
    input_dir = Path(__file__).parent.parent / args.input_dir
    output_dir = Path(__file__).parent.parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        'documents': ('documents_combined.csv', improve_documents_dataset),
        'sentiment': ('sentiment_combined.csv', improve_sentiment_dataset),
        'entities': ('entity_extraction_combined.csv', improve_entity_extraction_dataset),
        'demand': ('demand_forecasting_combined.csv', improve_demand_forecasting_dataset),
        'invoices': ('invoice_extraction_combined.csv', improve_invoice_extraction_dataset)
    }
    
    for dataset_type, (filename, improve_func) in datasets.items():
        if args.type in [dataset_type, 'all']:
            input_file = input_dir / filename
            if input_file.exists():
                output_file = output_dir / filename.replace('_combined.csv', '_improved.csv')
                try:
                    improve_func(str(input_file), str(output_file))
                except Exception as e:
                    print(f"✗ Error improving {dataset_type}: {e}")
            else:
                print(f"✗ File not found: {input_file}")

if __name__ == "__main__":
    main()

