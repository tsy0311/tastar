"""
Customer Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import datetime

class CustomerBase(BaseModel):
    """Base customer schema"""
    customer_code: str
    name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    customer_type: Optional[str] = None
    industry: Optional[str] = None
    segment: Optional[str] = None

class CustomerCreate(CustomerBase):
    """Customer creation schema"""
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    currency_code: str = "USD"

class CustomerUpdate(BaseModel):
    """Customer update schema"""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address_line1: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    currency_code: Optional[str] = None
    status: Optional[str] = None

class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: str
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    currency_code: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True




