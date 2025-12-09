"""
Invoice Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class InvoiceLineItemBase(BaseModel):
    """Base invoice line item schema"""
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None

class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Invoice line item creation schema"""
    product_code: Optional[str] = None
    product_name: Optional[str] = None

class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Invoice line item response schema"""
    id: str
    line_number: int
    line_total: Decimal
    tax_amount: Decimal
    
    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    """Base invoice schema"""
    customer_id: str
    invoice_date: date
    due_date: date
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    """Invoice creation schema"""
    line_items: List[InvoiceLineItemCreate]

class InvoiceUpdate(BaseModel):
    """Invoice update schema"""
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    """Invoice response schema"""
    id: str
    invoice_number: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: str
    currency_code: str
    line_items: List[InvoiceLineItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

