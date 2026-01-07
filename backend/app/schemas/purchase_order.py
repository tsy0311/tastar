"""
Purchase Order Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class POLineItemBase(BaseModel):
    line_number: int
    material_id: Optional[str] = None
    material_code: Optional[str] = None
    material_description: str
    quantity_ordered: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    expected_delivery_date: Optional[date] = None

class POLineItemCreate(POLineItemBase):
    pass

class POLineItemResponse(POLineItemBase):
    id: str
    quantity_received: Decimal = Decimal("0")
    quantity_pending: Decimal
    line_total: Decimal
    received_date: Optional[date] = None
    status: str = "pending"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    po_number: str = Field(..., max_length=100)
    po_type: str = "standard"
    supplier_id: str
    po_date: date
    required_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_terms: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    currency_code: str = "USD"
    exchange_rate: Decimal = Decimal("1")

class PurchaseOrderCreate(PurchaseOrderBase):
    line_items: List[POLineItemCreate]

class PurchaseOrderUpdate(BaseModel):
    po_date: Optional[date] = None
    required_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_terms: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    status: Optional[str] = None
    approval_status: Optional[str] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: str
    company_id: str
    supplier_id: str
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    shipping_amount: Decimal = Decimal("0")
    total_amount: Decimal
    status: str = "draft"
    approval_status: Optional[str] = None
    line_items: List[POLineItemResponse] = []
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

