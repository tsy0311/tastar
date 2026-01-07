"""
Script to prepare training data from database
"""
import argparse
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.connection import get_db
from app.database.models import Document, Invoice, PurchaseOrder, Quotation, Bill

def prepare_document_classification_data(output_path: str = None):
    """Prepare document classification training data from database"""
    if output_path is None:
        output_path = Path(__file__).parent.parent / 'data' / 'processed' / 'document_classification.csv'
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    db = next(get_db())
    
    data = []
    
    # Get documents with OCR text
    documents = db.query(Document).filter(
        Document.extracted_data.isnot(None),
        Document.document_type.isnot(None)
    ).all()
    
    for doc in documents:
        # Extract text from document
        text = ""
        if doc.extracted_data and isinstance(doc.extracted_data, dict):
            text_parts = []
            for key, value in doc.extracted_data.items():
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
            text = " ".join(text_parts)
        
        if text and doc.document_type:
            data.append({
                'text': text,
                'label': doc.document_type
            })
    
    # Also extract from structured documents
    # Invoices
    invoices = db.query(Invoice).filter(Invoice.notes.isnot(None)).limit(100).all()
    for inv in invoices:
        text = f"Invoice {inv.invoice_number} Date: {inv.invoice_date} Amount: {inv.total_amount}"
        if inv.notes:
            text += f" {inv.notes}"
        data.append({'text': text, 'label': 'invoice'})
    
    # Purchase Orders
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.notes.isnot(None)).limit(100).all()
    for po in pos:
        text = f"Purchase Order {po.po_number} Date: {po.po_date} Amount: {po.total_amount}"
        if po.notes:
            text += f" {po.notes}"
        data.append({'text': text, 'label': 'purchase_order'})
    
    # Quotations
    quotes = db.query(Quotation).filter(Quotation.notes.isnot(None)).limit(100).all()
    for quote in quotes:
        text = f"Quotation {quote.quotation_number} Date: {quote.quotation_date} Amount: {quote.total_amount}"
        if quote.notes:
            text += f" {quote.notes}"
        data.append({'text': text, 'label': 'quotation'})
    
    # Bills
    bills = db.query(Bill).filter(Bill.notes.isnot(None)).limit(100).all()
    for bill in bills:
        text = f"Bill {bill.bill_number} Date: {bill.bill_date} Amount: {bill.total_amount}"
        if bill.notes:
            text += f" {bill.notes}"
        data.append({'text': text, 'label': 'bill'})
    
    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Prepared {len(df)} training samples")
        print(f"Label distribution:\n{df['label'].value_counts()}")
        print(f"Saved to {output_path}")
    else:
        print("No data found. Make sure you have documents in the database.")
    
    return df if data else None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare training data from database')
    parser.add_argument('--output', type=str, help='Output CSV path')
    parser.add_argument('--type', type=str, default='document_classification', 
                       help='Data type to prepare')
    
    args = parser.parse_args()
    
    if args.type == 'document_classification':
        prepare_document_classification_data(args.output)

