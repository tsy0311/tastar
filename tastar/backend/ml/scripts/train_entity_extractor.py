"""
Script to train entity extraction model
"""
import argparse
import pickle
from pathlib import Path
import sys
import re
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def extract_entities_rule_based(text: str) -> Dict[str, List[str]]:
    """Extract entities using regex patterns"""
    entities = {
        'invoice_numbers': re.findall(r'(?:invoice|inv)[\s#:]*([A-Z0-9\-]+)', text, re.IGNORECASE),
        'po_numbers': re.findall(r'(?:po|purchase\s*order)[\s#:]*([A-Z0-9\-]+)', text, re.IGNORECASE),
        'amounts': re.findall(r'\$[\d,]+\.?\d*', text),
        'dates': re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}', text),
        'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        'phones': re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
        'tax_ids': re.findall(r'(?:tax\s*id|ein|vat)[\s#:]*([A-Z0-9\-]+)', text, re.IGNORECASE),
    }
    return {k: v for k, v in entities.items() if v}

def train_model(output_dir: str = None):
    """Train/save entity extraction model (rule-based)"""
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'entity_extractor'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save rule-based extractor
    with open(output_dir / 'rule_based_extractor.pkl', 'wb') as f:
        pickle.dump(extract_entities_rule_based, f)
    
    print(f"✓ Rule-based entity extractor saved to {output_dir}")
    print("Note: Rule-based extractor doesn't require training data")
    
    return extract_entities_rule_based

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train entity extraction model')
    parser.add_argument('--output', type=str, help='Output directory for model')
    
    args = parser.parse_args()
    train_model(output_dir=args.output)

