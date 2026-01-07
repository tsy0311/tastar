"""
Supplier Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class SupplierBase(BaseModel):
    supplier_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None
    currency_code: str = "USD"
    credit_limit: Optional[Decimal] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None
    currency_code: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    status: Optional[str] = None

class SupplierResponse(SupplierBase):
    id: str
    company_id: str
    on_time_delivery_rate: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    average_rating: Optional[Decimal] = None
    total_orders: int = 0
    total_spent: Decimal = Decimal("0")
    status: str = "active"
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

