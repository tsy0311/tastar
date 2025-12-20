"""
Bill (Accounts Payable) Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class BillBase(BaseModel):
    bill_number: str = Field(..., max_length=100)
    vendor_invoice_number: Optional[str] = None
    supplier_id: str
    purchase_order_id: Optional[str] = None
    bill_date: date
    due_date: date
    notes: Optional[str] = None
    attachment_url: Optional[str] = None
    currency_code: str = "USD"

class BillCreate(BillBase):
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total_amount: Decimal

class BillUpdate(BaseModel):
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    attachment_url: Optional[str] = None
    status: Optional[str] = None
    approval_status: Optional[str] = None

class BillResponse(BillBase):
    id: str
    company_id: str
    supplier_id: str
    purchase_order_id: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    total_amount: Decimal
    paid_amount: Decimal = Decimal("0")
    balance_amount: Decimal
    status: str = "draft"
    approval_status: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

