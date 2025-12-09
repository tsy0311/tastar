"""
Payment Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class PaymentAllocationCreate(BaseModel):
    """Payment allocation creation schema"""
    invoice_id: str
    amount: Decimal

class PaymentAllocationResponse(BaseModel):
    """Payment allocation response schema"""
    id: str
    invoice_id: Optional[str] = None
    allocated_amount: Decimal
    allocation_date: date
    
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    """Base payment schema"""
    payment_type: str
    amount: Decimal
    payment_date: date
    payment_method: str
    payment_reference: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Payment creation schema"""
    customer_id: Optional[str] = None
    allocations: Optional[List[PaymentAllocationCreate]] = None

class PaymentResponse(PaymentBase):
    """Payment response schema"""
    id: str
    payment_number: str
    customer_id: Optional[str] = None
    status: str
    currency_code: str
    allocations: List[PaymentAllocationResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

