"""
Utility functions for loading training data
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import requests
import zipfile
import io
from sqlalchemy import create_engine
from app.core.config import settings

def load_document_data(limit: Optional[int] = None) -> pd.DataFrame:
    """
    Load document classification data from database or CSV
    
    Args:
        limit: Maximum number of samples to load
        
    Returns:
        DataFrame with 'text' and 'label' columns (always returns a DataFrame, never None)
    """
    # Try to load from database first
    try:
        from app.database.connection import get_db
        from app.database.models import Document
        
        db = next(get_db())
        query = db.query(Document).filter(
            Document.extracted_data.isnot(None),
            Document.document_type.isnot(None)
        )
        
        if limit:
            query = query.limit(limit)
        
        docs = query.all()
        
        if docs:
            data = []
            for doc in docs:
                # Get text from extracted_data or file
                text = ""
                if doc.extracted_data and isinstance(doc.extracted_data, dict):
                    # Combine extracted text fields
                    text_parts = []
                    for key, value in doc.extracted_data.items():
                        if isinstance(value, str) and len(value) > 0:
                            text_parts.append(f"{key}: {value}")
                    text = " ".join(text_parts)
                
                if text:
                    data.append({
                        'text': text,
                        'label': doc.document_type
                    })
            
            if data:
                return pd.DataFrame(data)
    except Exception as e:
        print(f"Could not load from database: {e}")
    
    # Fallback to CSV
    csv_path = Path(__file__).parent.parent / 'data' / 'processed' / 'document_classification.csv'
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if limit:
            df = df.head(limit)
        return df
    
    # Try to download from public datasets
    print("No local data found. Attempting to download sample data from public datasets...")
    downloaded_df = _download_sample_data()
    if downloaded_df is not None and len(downloaded_df) > 0:
        # Save downloaded data for future use
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        downloaded_df.to_csv(csv_path, index=False)
        print(f"Downloaded {len(downloaded_df)} samples. Saved to {csv_path}")
        if limit:
            downloaded_df = downloaded_df.head(limit)
        return downloaded_df
    
    # Generate sample data if download fails (always returns a DataFrame)
    print("Download failed. Generating sample data...")
    sample_df = _generate_sample_data()
    # Ensure we always return a DataFrame (should never be None, but double-check)
    assert sample_df is not None, "Sample data generation failed"
    assert len(sample_df) > 0, "Sample data is empty"
    if limit:
        sample_df = sample_df.head(limit)
    return sample_df

def _generate_sample_data() -> pd.DataFrame:
    """Generate sample training data"""
    samples = [
        # Invoices
        ("Invoice #INV-001\nDate: 2024-01-15\nAmount Due: $1,500.00\nPayment Terms: Net 30", "invoice"),
        ("INVOICE\nBill To: ABC Company\nTotal Amount: $2,300.50\nDue Date: 2024-02-15", "invoice"),
        ("Invoice Number: 12345\nInvoice Date: 01/15/2024\nSubtotal: $1,000\nTax: $100\nTotal: $1,100", "invoice"),
        
        # Purchase Orders
        ("PURCHASE ORDER\nPO Number: PO-2024-001\nSupplier: XYZ Corp\nDelivery Date: 2024-02-01", "purchase_order"),
        ("Purchase Order #PO-123\nOrder Date: 2024-01-20\nVendor: Supplier ABC\nItems: 100 units", "purchase_order"),
        
        # Receipts
        ("RECEIPT\nThank you for your payment\nAmount Paid: $500.00\nPayment Date: 2024-01-10", "receipt"),
        ("Payment Receipt\nTransaction ID: TXN-789\nPaid Amount: $750.25\nStatus: Paid", "receipt"),
        
        # Quotations
        ("QUOTATION\nQuote Number: QT-2024-001\nValid Until: 2024-02-15\nEstimated Cost: $5,000", "quotation"),
        ("Quote #QT-123\nQuote Date: 2024-01-15\nTotal Estimate: $3,500.00\nValid for 30 days", "quotation"),
        
        # Delivery Orders
        ("DELIVERY ORDER\nDO Number: DO-001\nDelivery Date: 2024-01-25\nReceived By: John Doe", "delivery_order"),
    ]
    
    # Expand with variations
    expanded = []
    for text, label in samples:
        expanded.append((text, label))
        expanded.append((text.lower(), label))
        expanded.append((text.upper(), label))
    
    return pd.DataFrame(expanded, columns=['text', 'label'])

def _download_sample_data() -> Optional[pd.DataFrame]:
    """
    Download sample document classification data from public sources
    
    Sources tried:
    1. Hugging Face datasets (document classification)
    2. Kaggle datasets (if kaggle package available)
    3. Google Drive public links
    """
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Try Hugging Face datasets first (easiest, no auth needed)
    try:
        print("Trying Hugging Face datasets...")
        from datasets import load_dataset
        
        # Try multiple document-related datasets
        hf_datasets_to_try = [
            # Text classification datasets that can be adapted
            ("ag_news", "train[:100]"),  # News articles - can adapt to business docs
            ("yelp_review_full", "train[:100]"),  # Reviews - can adapt
            ("amazon_polarity", "train[:100]"),  # Product reviews
        ]
        
        for dataset_name, split in hf_datasets_to_try:
            try:
                print(f"  Trying {dataset_name}...")
                # Add timeout and error handling
                import signal
                dataset = load_dataset(dataset_name, split=split, trust_remote_code=True)
                
                data = []
                for item in dataset:
                    # Extract text
                    text = item.get('text', '') or item.get('content', '') or str(item.get('title', '')) + ' ' + str(item.get('text', ''))
                    
                    if not text or len(str(text)) < 20:
                        continue
                    
                    # Classify based on keywords (simple adaptation)
                    text_lower = str(text).lower()
                    if any(word in text_lower for word in ['invoice', 'bill', 'payment due', 'amount due']):
                        label = 'invoice'
                    elif any(word in text_lower for word in ['purchase order', 'po number', 'order number', 'supplier']):
                        label = 'purchase_order'
                    elif any(word in text_lower for word in ['receipt', 'payment received', 'thank you for payment']):
                        label = 'receipt'
                    elif any(word in text_lower for word in ['quotation', 'quote', 'estimate', 'proposal']):
                        label = 'quotation'
                    elif any(word in text_lower for word in ['delivery', 'delivery order', 'shipping']):
                        label = 'delivery_order'
                    else:
                        label = 'general'
                    
                    # Create business document format
                    business_text = f"{text[:500]}"
                    data.append({'text': business_text, 'label': label})
                
                if len(data) >= 20:  # Need at least 20 samples
                    df = pd.DataFrame(data)
                    print(f"  ✓ Loaded {len(df)} samples from {dataset_name}")
                    return df
                else:
                    print(f"  {dataset_name}: Only got {len(data)} samples, need at least 20")
            except Exception as e:
                print(f"  {dataset_name} failed: {str(e)[:100]}...")  # Truncate long errors
                continue
    except ImportError:
        print("  Hugging Face datasets not installed. Install with: pip install datasets")
        print("  Falling back to sample data generation...")
    except Exception as e:
        print(f"  Hugging Face download failed: {str(e)[:100]}...")
        print("  Falling back to sample data generation...")
    
    # Try Kaggle datasets
    try:
        print("Trying Kaggle datasets...")
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        # Search for document classification datasets
        # Example: Download a document classification dataset
        # Note: You need to accept competition/dataset rules on Kaggle first
        try:
            # Try a popular document classification dataset
            # Replace with actual dataset name once you find one
            dataset_name = "document-classification"  # Placeholder
            api.dataset_download_files(dataset_name, path=str(data_dir), unzip=True)
            
            # Look for CSV files
            csv_files = list(data_dir.glob("*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
                # Ensure it has 'text' and 'label' columns
                if 'text' in df.columns and 'label' in df.columns:
                    print(f"✓ Loaded {len(df)} samples from Kaggle")
                    return df[['text', 'label']]
        except Exception as e:
            print(f"  Kaggle download failed: {e}")
    except ImportError:
        print("  Kaggle API not installed. Install with: pip install kaggle")
    except Exception as e:
        print(f"  Kaggle authentication/download failed: {e}")
    
    # Try Google Drive public link
    try:
        print("Trying Google Drive...")
        # Example: Download from a public Google Drive link
        # Replace with actual dataset link
        file_id = "1ABC123XYZ"  # Placeholder - replace with actual file ID
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Try to parse as CSV
            try:
                df = pd.read_csv(io.StringIO(response.text))
                if 'text' in df.columns and 'label' in df.columns:
                    print(f"✓ Loaded {len(df)} samples from Google Drive")
                    return df[['text', 'label']]
            except:
                # Try as zip file
                try:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        for file_name in z.namelist():
                            if file_name.endswith('.csv'):
                                with z.open(file_name) as f:
                                    df = pd.read_csv(f)
                                    if 'text' in df.columns and 'label' in df.columns:
                                        print(f"✓ Loaded {len(df)} samples from Google Drive zip")
                                        return df[['text', 'label']]
                except:
                    pass
    except Exception as e:
        print(f"  Google Drive download failed: {e}")
    
    # Try a curated public dataset URL
    try:
        print("Trying public dataset URL...")
        # Example: A publicly hosted CSV file
        # You can replace this with an actual dataset URL
        dataset_urls = [
            # Add actual dataset URLs here
            # "https://example.com/datasets/document-classification.csv",
        ]
        
        for url in dataset_urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    df = pd.read_csv(io.StringIO(response.text))
                    if 'text' in df.columns and 'label' in df.columns:
                        print(f"✓ Loaded {len(df)} samples from public URL")
                        return df[['text', 'label']]
            except:
                continue
    except Exception as e:
        print(f"  Public URL download failed: {e}")
    
    return None

def download_kaggle_dataset(dataset_name: str, output_dir: Path = None) -> Optional[pd.DataFrame]:
    """
    Download a specific Kaggle dataset
    
    Args:
        dataset_name: Kaggle dataset name (e.g., "username/dataset-name")
        output_dir: Directory to save the dataset
        
    Returns:
        DataFrame if successful, None otherwise
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_name, path=str(output_dir), unzip=True)
        
        # Find CSV files
        csv_files = list(output_dir.glob("*.csv"))
        if csv_files:
            df = pd.read_csv(csv_files[0])
            return df
        
    except ImportError:
        print("Kaggle API not installed. Install with: pip install kaggle")
        print("Then authenticate: kaggle.json in ~/.kaggle/")
    except Exception as e:
        print(f"Error downloading Kaggle dataset: {e}")
    
    return None

def download_huggingface_dataset(dataset_name: str, split: str = "train", limit: int = None) -> pd.DataFrame:
    """
    Download a Hugging Face dataset
    
    Args:
        dataset_name: Hugging Face dataset name
        split: Dataset split to use
        limit: Maximum number of samples
        
    Returns:
        DataFrame with 'text' and 'label' columns
    """
    try:
        from datasets import load_dataset
        
        dataset = load_dataset(dataset_name, split=split)
        if limit:
            dataset = dataset.select(range(min(limit, len(dataset))))
        
        data = []
        for item in dataset:
            text = item.get('text', '') or item.get('content', '') or str(item)
            # Preserve numeric labels (don't convert to string yet)
            label = item.get('label', None)
            if label is None:
                label = item.get('type', 'general')
            
            if text:
                data.append({
                    'text': str(text),
                    'label': label  # Keep original type (int/str)
                })
        
        if data:
            return pd.DataFrame(data)
            
    except ImportError:
        print("Hugging Face datasets not installed. Install with: pip install datasets")
        # Return sample data instead of None
        return _generate_sample_data()
    except Exception as e:
        print(f"Error loading Hugging Face dataset: {e}")
        # Return sample data instead of None
        return _generate_sample_data()
    
    # If we get here, return sample data
    return _generate_sample_data()

def load_sentiment_data(limit: Optional[int] = None) -> pd.DataFrame:
    """Load sentiment analysis training data"""
    # TODO: Load from database (customer emails, reviews, feedback)
    csv_path = Path(__file__).parent.parent / 'data' / 'processed' / 'sentiment.csv'
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if limit:
            df = df.head(limit)
        return df
    
    # Sample data
    samples = [
        ("Thank you for the excellent service!", "positive"),
        ("Great product, very satisfied!", "positive"),
        ("I'm very disappointed with the quality", "negative"),
        ("This is terrible, I want a refund", "negative"),
        ("The order was delivered on time", "neutral"),
    ]
    
    return pd.DataFrame(samples, columns=['text', 'label'])

