"""
Script to train invoice data extraction model
"""
import argparse
import pickle
from pathlib import Path
import sys
import re
import json
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def extract_invoice_data(text: str) -> Dict:
    """Extract structured data from invoice text"""
    result = {
        'invoice_number': None,
        'invoice_date': None,
        'due_date': None,
        'vendor_name': None,
        'customer_name': None,
        'subtotal': None,
        'tax': None,
        'total': None,
        'payment_terms': None,
        'line_items': []
    }
    
    # Extract invoice number
    inv_match = re.search(r'invoice\s*(?:number|#|no\.?)[\s:]*([A-Z0-9\-]+)', text, re.IGNORECASE)
    if inv_match:
        result['invoice_number'] = inv_match.group(1)
    
    # Extract dates
    dates = re.findall(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})', text)
    if dates:
        result['invoice_date'] = dates[0]
        if len(dates) > 1:
            result['due_date'] = dates[1]
    
    # Extract amounts
    subtotal_match = re.search(r'subtotal[\s:]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
    tax_match = re.search(r'tax[\s:]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
    total_match = re.search(r'total[\s:]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
    
    if subtotal_match:
        result['subtotal'] = float(subtotal_match.group(1).replace(',', ''))
    if tax_match:
        result['tax'] = float(tax_match.group(1).replace(',', ''))
    if total_match:
        result['total'] = float(total_match.group(1).replace(',', ''))
    
    # Extract payment terms
    terms_match = re.search(r'payment\s*terms?[\s:]*([^\n]+)', text, re.IGNORECASE)
    if terms_match:
        result['payment_terms'] = terms_match.group(1).strip()
    
    return result

def train_model(output_dir: str = None):
    """Train/save invoice extraction model"""
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'invoice_extractor'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save extractor
    with open(output_dir / 'invoice_extractor.pkl', 'wb') as f:
        pickle.dump(extract_invoice_data, f)
    
    print(f"✓ Invoice extractor saved to {output_dir}")
    
    return extract_invoice_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train invoice extraction model')
    parser.add_argument('--output', type=str, help='Output directory for model')
    
    args = parser.parse_args()
    train_model(output_dir=args.output)

