"""
Quotation Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class QuotationLineItemBase(BaseModel):
    line_number: int
    description: str
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    material_id: Optional[str] = None
    job_id: Optional[str] = None

class QuotationLineItemCreate(QuotationLineItemBase):
    pass

class QuotationLineItemResponse(QuotationLineItemBase):
    id: str
    discount_amount: Decimal = Decimal("0")
    line_total: Decimal
    tax_amount: Decimal = Decimal("0")
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuotationBase(BaseModel):
    quotation_number: str = Field(..., max_length=100)
    customer_id: str
    quotation_date: date
    valid_until: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    currency_code: str = "USD"
    exchange_rate: Decimal = Decimal("1")

class QuotationCreate(QuotationBase):
    line_items: List[QuotationLineItemCreate]

class QuotationUpdate(BaseModel):
    quotation_date: Optional[date] = None
    valid_until: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    status: Optional[str] = None
    approval_status: Optional[str] = None

class QuotationResponse(QuotationBase):
    id: str
    company_id: str
    customer_id: str
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    shipping_amount: Decimal = Decimal("0")
    total_amount: Decimal
    status: str = "draft"
    approval_status: Optional[str] = None
    line_items: List[QuotationLineItemResponse] = []
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

