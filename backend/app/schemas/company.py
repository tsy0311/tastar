"""
Company Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyResponse(BaseModel):
    """Company response schema"""
    id: str
    name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    country: str
    currency_code: str
    timezone: str
    locale: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CompanyUpdate(BaseModel):
    """Company update schema"""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    currency_code: Optional[str] = None

