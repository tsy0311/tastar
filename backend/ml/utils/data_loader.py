"""
Utility functions for loading training data
"""
import pandas as pd
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from app.core.config import settings

def load_document_data(limit: Optional[int] = None) -> pd.DataFrame:
    """
    Load document classification data from database or CSV
    
    Args:
        limit: Maximum number of samples to load
        
    Returns:
        DataFrame with 'text' and 'label' columns
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
    
    # Generate sample data if nothing found
    print("No training data found. Generating sample data...")
    return _generate_sample_data()

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

