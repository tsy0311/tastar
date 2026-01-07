#!/usr/bin/env python3
"""
Download datasets for ML model training
Supports Hugging Face, Kaggle, and direct URLs
"""
import argparse
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml.utils.data_loader import (
    download_huggingface_dataset,
    download_kaggle_dataset,
    load_document_data
)

def download_document_datasets(output_dir: str = None, limit: int = 500):
    """Download document classification datasets"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Document Classification Datasets")
    print("=" * 60)
    
    datasets = []
    
    # 1. Hugging Face - Synthetic Invoices
    print("\n1. Trying Hugging Face: rcds/synthetic-invoices")
    try:
        df = download_huggingface_dataset("rcds/synthetic-invoices", limit=limit)
        if df is not None and not df.empty:
            datasets.append(df)
            print(f"   ✓ Downloaded {len(df)} samples")
        else:
            print("   ✗ Dataset not available or empty")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Hugging Face - AG News (can be adapted)
    print("\n2. Trying Hugging Face: ag_news (adaptable)")
    try:
        df = download_huggingface_dataset("ag_news", split="train", limit=limit)
        if df is not None and not df.empty:
            # Adapt labels for document classification
            if 'text' in df.columns and 'label' in df.columns:
                # AG News labels: 0=World, 1=Sports, 2=Business, 3=Sci/Tech
                # Map to document types based on keywords in text
                def map_to_document_type(text, original_label):
                    text_lower = str(text).lower()
                    # Business news often contains invoice/PO keywords
                    if original_label == 2 or any(word in text_lower for word in ['invoice', 'bill', 'payment', 'order', 'purchase', 'receipt', 'quotation', 'delivery']):
                        if any(word in text_lower for word in ['invoice', 'bill', 'payment due']):
                            return 'invoice'
                        elif any(word in text_lower for word in ['purchase order', 'po number', 'supplier']):
                            return 'purchase_order'
                        elif any(word in text_lower for word in ['receipt', 'payment received']):
                            return 'receipt'
                        elif any(word in text_lower for word in ['quotation', 'quote', 'estimate']):
                            return 'quotation'
                        elif any(word in text_lower for word in ['delivery', 'shipping']):
                            return 'delivery_order'
                        else:
                            return 'general'
                    else:
                        return 'general'
                
                df['label'] = df.apply(lambda row: map_to_document_type(row['text'], row['label']), axis=1)
                datasets.append(df[['text', 'label']])
                print(f"   ✓ Downloaded {len(df)} samples (mapped to document types)")
        else:
            print("   ✗ Dataset not available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 3. Local database data
    print("\n3. Loading from local database...")
    try:
        df = load_document_data()
        if df is not None and not df.empty:
            datasets.append(df)
            print(f"   ✓ Loaded {len(df)} samples from database")
        else:
            print("   ✗ No data in database")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Combine all datasets
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        output_file = output_dir / 'documents_combined.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined dataset saved: {output_file}")
        print(f"  Total samples: {len(combined_df)}")
        print(f"  Label distribution:")
        print(combined_df['label'].value_counts())
        return combined_df
    else:
        print("\n✗ No datasets downloaded. Creating sample data...")
        # Create sample data
        sample_data = {
            'text': [
                'Invoice #001\nDate: 2024-01-01\nAmount: $100\nCustomer: ABC Corp',
                'Purchase Order PO-001\nSupplier: XYZ Ltd\nItems: 10 units\nTotal: $500',
                'Receipt #RCP-001\nPayment: $50\nDate: 2024-01-15\nThank you!',
                'Quotation QT-001\nDate: 2024-01-20\nEstimate: $1000\nValid until: 2024-02-20',
                'Delivery Order DO-001\nDate: 2024-01-25\nReceived: 10 units\nStatus: Complete',
            ] * 20,  # Repeat to get 100 samples
            'label': [
                'invoice', 'purchase_order', 'receipt', 'quotation', 'delivery_order'
            ] * 20
        }
        df = pd.DataFrame(sample_data)
        output_file = output_dir / 'documents_sample.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Sample dataset created: {output_file}")
        return df

def download_sentiment_datasets(output_dir: str = None, limit: int = 500):
    """Download sentiment analysis datasets"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Sentiment Analysis Datasets")
    print("=" * 60)
    
    datasets = []
    
    # 1. IMDB Reviews
    print("\n1. Trying Hugging Face: imdb")
    try:
        df = download_huggingface_dataset("imdb", split="train", limit=limit)
        if df is not None and not df.empty:
            # Map to sentiment labels
            if 'label' in df.columns:
                # Convert label to int if it's a string
                df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
                df['sentiment'] = df['label'].map({0: 'negative', 1: 'positive'})
                df = df[['text', 'sentiment']].rename(columns={'sentiment': 'label'})
                # Remove any rows with missing labels
                df = df.dropna(subset=['label'])
                datasets.append(df)
                print(f"   ✓ Downloaded {len(df)} samples")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Yelp Reviews
    print("\n2. Trying Hugging Face: yelp_review_full")
    try:
        df = download_huggingface_dataset("yelp_review_full", split="train", limit=limit)
        if df is not None and not df.empty:
            if 'label' in df.columns:
                # Convert label to int if it's a string (yelp uses 0-4 ratings)
                df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
                # Map 5-star ratings to sentiment (0-1=negative, 2=neutral, 3-4=positive)
                df['sentiment'] = df['label'].apply(
                    lambda x: 'positive' if x >= 3 else ('neutral' if x == 2 else 'negative')
                )
                # Filter out neutral for binary classification
                df = df[df['sentiment'] != 'neutral']
                df = df[['text', 'sentiment']].rename(columns={'sentiment': 'label'})
                datasets.append(df)
                print(f"   ✓ Downloaded {len(df)} samples")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Combine
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        output_file = output_dir / 'sentiment_combined.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined dataset saved: {output_file}")
        print(f"  Total samples: {len(combined_df)}")
        print(f"  Label distribution:")
        print(combined_df['label'].value_counts())
        return combined_df
    else:
        print("\n✗ No datasets downloaded")
        return None

def download_entity_extraction_datasets(output_dir: str = None, limit: int = 500):
    """Download Named Entity Recognition (NER) datasets"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Entity Extraction (NER) Datasets")
    print("=" * 60)
    
    datasets = []
    
    # 1. Hugging Face - CoNLL-2003 (English NER)
    print("\n1. Trying Hugging Face: conll2003")
    try:
        from datasets import load_dataset
        dataset = load_dataset("conll2003", split="train")
        if limit:
            dataset = dataset.select(range(min(limit, len(dataset))))
        
        data = []
        for item in dataset:
            tokens = item.get('tokens', [])
            ner_tags = item.get('ner_tags', [])
            
            if tokens and ner_tags:
                # Convert to BIO format
                text = " ".join(tokens)
                entities = []
                current_entity = None
                start_idx = 0
                
                for i, (token, tag) in enumerate(zip(tokens, ner_tags)):
                    # CoNLL-2003 tags: 0=O, 1=B-PER, 2=I-PER, 3=B-ORG, 4=I-ORG, 5=B-LOC, 6=I-LOC, 7=B-MISC, 8=I-MISC
                    tag_map = {0: 'O', 1: 'B-PER', 2: 'I-PER', 3: 'B-ORG', 4: 'I-ORG', 
                              5: 'B-LOC', 6: 'I-LOC', 7: 'B-MISC', 8: 'I-MISC'}
                    tag_str = tag_map.get(tag, 'O')
                    
                    if tag_str.startswith('B-'):
                        if current_entity:
                            entities.append({
                                'text': " ".join(tokens[current_entity['start']:i]),
                                'label': current_entity['label'],
                                'start': current_entity['start'],
                                'end': i
                            })
                        current_entity = {'start': i, 'label': tag_str[2:]}
                    elif tag_str == 'O' and current_entity:
                        entities.append({
                            'text': " ".join(tokens[current_entity['start']:i]),
                            'label': current_entity['label'],
                            'start': current_entity['start'],
                            'end': i
                        })
                        current_entity = None
                
                if current_entity:
                    entities.append({
                        'text': " ".join(tokens[current_entity['start']:]),
                        'label': current_entity['label'],
                        'start': current_entity['start'],
                        'end': len(tokens)
                    })
                
                # Adapt to business entities
                business_entities = []
                for ent in entities:
                    # Map to business-relevant entities
                    if ent['label'] in ['PER', 'ORG']:
                        business_entities.append({
                            'text': text,
                            'entity': ent['text'],
                            'label': 'company_name' if ent['label'] == 'ORG' else 'person_name',
                            'start': ent['start'],
                            'end': ent['end']
                        })
                
                if business_entities:
                    data.append({
                        'text': text,
                        'entities': str(business_entities)
                    })
        
        if data:
            df = pd.DataFrame(data)
            datasets.append(df)
            print(f"   ✓ Downloaded {len(df)} samples")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Hugging Face - tner/tweetner7 (can be adapted)
    print("\n2. Trying Hugging Face: tner/tweetner7")
    try:
        df = download_huggingface_dataset("tner/tweetner7", split="train", limit=limit)
        if df is not None and not df.empty:
            # Adapt to business entities
            datasets.append(df)
            print(f"   ✓ Downloaded {len(df)} samples")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 3. Generate sample business entity data
    print("\n3. Generating sample business entity data...")
    sample_data = []
    sample_texts = [
        "Invoice #INV-001 dated 2024-01-15 for $1,500.00 from ABC Corporation. Contact: john.doe@abc.com or call 555-1234.",
        "Purchase Order PO-2024-001 to XYZ Ltd. Delivery to 123 Main St, New York, NY 10001. Tax ID: 12-3456789.",
        "Payment of $2,300.50 received from Tech Solutions Inc. Reference: PAY-789. Date: 2024-02-15.",
        "Quotation QT-001 for $5,000.00 from Supplier ABC. Valid until 2024-02-20. Contact: sales@supplier.com.",
        "Delivery Order DO-001 to Manufacturing Corp. Address: 456 Industrial Ave, Los Angeles, CA 90001."
    ] * (limit // 5 + 1)
    
    for text in sample_texts[:limit]:
        entities = []
        import re
        
        # Extract invoice numbers
        for match in re.finditer(r'(?:invoice|inv)[\s#:]*([A-Z0-9\-]+)', text, re.IGNORECASE):
            entities.append({'entity': match.group(1), 'label': 'invoice_number', 'start': match.start(), 'end': match.end()})
        
        # Extract amounts
        for match in re.finditer(r'\$[\d,]+\.?\d*', text):
            entities.append({'entity': match.group(0), 'label': 'amount', 'start': match.start(), 'end': match.end()})
        
        # Extract dates
        for match in re.finditer(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', text):
            entities.append({'entity': match.group(0), 'label': 'date', 'start': match.start(), 'end': match.end()})
        
        # Extract emails
        for match in re.finditer(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            entities.append({'entity': match.group(0), 'label': 'email', 'start': match.start(), 'end': match.end()})
        
        # Extract phone numbers
        for match in re.finditer(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            entities.append({'entity': match.group(0), 'label': 'phone', 'start': match.start(), 'end': match.end()})
        
        # Extract company names (simple heuristic)
        company_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Corporation|Corp|Inc|Ltd|LLC|Company|Co\.)',
            r'\b([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)*)\s+(?:CORP|INC|LTD)'
        ]
        for pattern in company_patterns:
            for match in re.finditer(pattern, text):
                entities.append({'entity': match.group(0), 'label': 'company_name', 'start': match.start(), 'end': match.end()})
        
        if entities:
            sample_data.append({
                'text': text,
                'entities': str(entities)
            })
    
    if sample_data:
        df = pd.DataFrame(sample_data)
        datasets.append(df)
        print(f"   ✓ Generated {len(df)} sample samples")
    
    # Combine all datasets
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        output_file = output_dir / 'entity_extraction_combined.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined dataset saved: {output_file}")
        print(f"  Total samples: {len(combined_df)}")
        return combined_df
    else:
        print("\n✗ No datasets downloaded")
        return None

def download_demand_forecasting_datasets(output_dir: str = None, limit: int = 500):
    """Download time series datasets for demand forecasting"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Demand Forecasting (Time Series) Datasets")
    print("=" * 60)
    
    datasets = []
    
    # 1. Generate synthetic time series data (realistic business demand patterns)
    print("\n1. Generating synthetic demand forecasting data...")
    import numpy as np
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(limit)]
    
    # Create multiple time series with different patterns
    time_series_data = []
    
    for material_id in ['MAT-001', 'MAT-002', 'MAT-003']:
        # Base demand with trend
        base_demand = 100 if material_id == 'MAT-001' else (150 if material_id == 'MAT-002' else 80)
        trend = np.linspace(0, 20, limit) if material_id == 'MAT-001' else np.linspace(0, -10, limit)
        
        # Weekly seasonality
        seasonal = 15 * np.sin(2 * np.pi * np.arange(limit) / 7)
        
        # Monthly seasonality
        monthly = 10 * np.sin(2 * np.pi * np.arange(limit) / 30)
        
        # Random noise
        noise = np.random.normal(0, 5, limit)
        
        demand = base_demand + trend + seasonal + monthly + noise
        demand = np.maximum(demand, 0)  # No negative demand
        
        for i, (date, d) in enumerate(zip(dates, demand)):
            time_series_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'demand': int(d),
                'material_id': material_id,
                'day_of_week': date.weekday(),
                'month': date.month,
                'day_of_month': date.day
            })
    
    if time_series_data:
        df = pd.DataFrame(time_series_data)
        datasets.append(df)
        print(f"   ✓ Generated {len(df)} time series samples")
    
    # 2. Try to load from local database (if available)
    print("\n2. Loading from local database...")
    try:
        from app.database.connection import get_db
        from app.database.models import PurchaseOrder, Invoice
        
        db = next(get_db())
        
        # Get historical order data
        orders = db.query(PurchaseOrder).filter(
            PurchaseOrder.created_at.isnot(None)
        ).limit(limit).all()
        
        if orders:
            order_data = []
            for order in orders:
                order_data.append({
                    'date': order.created_at.strftime('%Y-%m-%d') if order.created_at else None,
                    'demand': order.total_amount or 0,
                    'material_id': f"MAT-{order.id}",
                    'day_of_week': order.created_at.weekday() if order.created_at else 0,
                    'month': order.created_at.month if order.created_at else 1,
                    'day_of_month': order.created_at.day if order.created_at else 1
                })
            
            if order_data:
                df = pd.DataFrame(order_data)
                datasets.append(df)
                print(f"   ✓ Loaded {len(df)} samples from database")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Combine all datasets
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        output_file = output_dir / 'demand_forecasting_combined.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined dataset saved: {output_file}")
        print(f"  Total samples: {len(combined_df)}")
        print(f"  Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
        return combined_df
    else:
        print("\n✗ No datasets downloaded")
        return None

def download_invoice_data_extraction_datasets(output_dir: str = None, limit: int = 500):
    """Download datasets for invoice data extraction"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Downloading Invoice Data Extraction Datasets")
    print("=" * 60)
    
    datasets = []
    
    # 1. Hugging Face - Invoice datasets
    print("\n1. Trying Hugging Face: invoice-related datasets")
    try:
        # Try to find invoice datasets
        hf_datasets = [
            "rcds/synthetic-invoices",
            "funcomics/invoice-dataset",
        ]
        
        for dataset_name in hf_datasets:
            try:
                df = download_huggingface_dataset(dataset_name, split="train", limit=limit)
                if df is not None and not df.empty:
                    datasets.append(df)
                    print(f"   ✓ Downloaded {len(df)} samples from {dataset_name}")
                    break
            except:
                continue
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Generate sample invoice data with structured fields
    print("\n2. Generating sample invoice extraction data...")
    sample_data = []
    
    invoice_templates = [
        {
            'text': """INVOICE
Invoice Number: INV-001
Invoice Date: 2024-01-15
Due Date: 2024-02-15

Bill To:
ABC Corporation
123 Business St
New York, NY 10001
Tax ID: 12-3456789

Ship To:
ABC Corporation
123 Business St
New York, NY 10001

Items:
1. Product A - Qty: 10 - Price: $100.00 - Total: $1,000.00
2. Product B - Qty: 5 - Price: $50.00 - Total: $250.00

Subtotal: $1,250.00
Tax (8%): $100.00
Shipping: $50.00
Total: $1,400.00

Payment Terms: Net 30
Contact: billing@abc.com
Phone: 555-1234""",
            'extracted_data': {
                'invoice_number': 'INV-001',
                'invoice_date': '2024-01-15',
                'due_date': '2024-02-15',
                'bill_to_company': 'ABC Corporation',
                'bill_to_address': '123 Business St, New York, NY 10001',
                'tax_id': '12-3456789',
                'subtotal': 1250.00,
                'tax': 100.00,
                'shipping': 50.00,
                'total': 1400.00,
                'payment_terms': 'Net 30',
                'contact_email': 'billing@abc.com',
                'contact_phone': '555-1234'
            }
        },
        {
            'text': """INVOICE #INV-002
Date: 01/15/2024
Due: 02/15/2024

Customer: XYZ Ltd
Address: 456 Commerce Ave, Los Angeles, CA 90001
EIN: 98-7654321

Line Items:
Item 1: Widget X - 20 units @ $75.00 = $1,500.00
Item 2: Widget Y - 15 units @ $60.00 = $900.00

Subtotal: $2,400.00
Sales Tax (10%): $240.00
Total Amount: $2,640.00

Terms: Net 45
Email: accounts@xyz.com
Tel: (555) 987-6543""",
            'extracted_data': {
                'invoice_number': 'INV-002',
                'invoice_date': '01/15/2024',
                'due_date': '02/15/2024',
                'bill_to_company': 'XYZ Ltd',
                'bill_to_address': '456 Commerce Ave, Los Angeles, CA 90001',
                'tax_id': '98-7654321',
                'subtotal': 2400.00,
                'tax': 240.00,
                'total': 2640.00,
                'payment_terms': 'Net 45',
                'contact_email': 'accounts@xyz.com',
                'contact_phone': '(555) 987-6543'
            }
        }
    ]
    
    # Generate variations
    for i in range(limit):
        template = invoice_templates[i % len(invoice_templates)]
        sample_data.append({
            'text': template['text'],
            'extracted_data': str(template['extracted_data']),
            'invoice_number': template['extracted_data'].get('invoice_number', ''),
            'invoice_date': template['extracted_data'].get('invoice_date', ''),
            'total_amount': template['extracted_data'].get('total', 0),
            'company_name': template['extracted_data'].get('bill_to_company', '')
        })
    
    if sample_data:
        df = pd.DataFrame(sample_data)
        datasets.append(df)
        print(f"   ✓ Generated {len(df)} sample invoice samples")
    
    # 3. Load from local database
    print("\n3. Loading from local database...")
    try:
        from app.database.connection import get_db
        from app.database.models import Invoice
        
        db = next(get_db())
        invoices = db.query(Invoice).filter(
            Invoice.extracted_data.isnot(None)
        ).limit(limit).all()
        
        if invoices:
            invoice_data = []
            for invoice in invoices:
                text = ""
                if invoice.extracted_data and isinstance(invoice.extracted_data, dict):
                    text = " ".join([f"{k}: {v}" for k, v in invoice.extracted_data.items() if v])
                
                if text:
                    invoice_data.append({
                        'text': text,
                        'extracted_data': str(invoice.extracted_data),
                        'invoice_number': invoice.invoice_number or '',
                        'invoice_date': str(invoice.invoice_date) if invoice.invoice_date else '',
                        'total_amount': float(invoice.total_amount) if invoice.total_amount else 0,
                        'company_name': invoice.customer_name or ''
                    })
            
            if invoice_data:
                df = pd.DataFrame(invoice_data)
                datasets.append(df)
                print(f"   ✓ Loaded {len(df)} samples from database")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Combine all datasets
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        output_file = output_dir / 'invoice_extraction_combined.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined dataset saved: {output_file}")
        print(f"  Total samples: {len(combined_df)}")
        return combined_df
    else:
        print("\n✗ No datasets downloaded")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download datasets for ML training')
    parser.add_argument('--type', type=str, 
                       choices=['documents', 'sentiment', 'entities', 'demand', 'invoices', 'all'],
                       default='all', help='Type of dataset to download')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--limit', type=int, default=500, 
                       help='Limit number of samples per dataset')
    
    args = parser.parse_args()
    
    if args.type in ['documents', 'all']:
        download_document_datasets(args.output, args.limit)
    
    if args.type in ['sentiment', 'all']:
        download_sentiment_datasets(args.output, args.limit)
    
    if args.type in ['entities', 'all']:
        download_entity_extraction_datasets(args.output, args.limit)
    
    if args.type in ['demand', 'all']:
        download_demand_forecasting_datasets(args.output, args.limit)
    
    if args.type in ['invoices', 'all']:
        download_invoice_data_extraction_datasets(args.output, args.limit)

if __name__ == "__main__":
    main()

