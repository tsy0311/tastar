"""
Transaction Matching Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TransactionMatchingCreate(BaseModel):
    purchase_order_id: Optional[str] = None
    delivery_order_id: Optional[str] = None
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None
    match_type: str = Field(..., description="two_way or three_way")
    tolerance_threshold: Optional[Decimal] = None

class TransactionMatchingResponse(BaseModel):
    id: str
    company_id: str
    purchase_order_id: Optional[str] = None
    delivery_order_id: Optional[str] = None
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None
    match_type: str
    match_status: str = "pending"
    match_confidence_score: Optional[Decimal] = None
    amount_variance: Optional[Decimal] = None
    quantity_variance: Optional[Decimal] = None
    date_variance: Optional[int] = None
    tolerance_threshold: Optional[Decimal] = None
    within_tolerance: Optional[bool] = None
    exception_reason: Optional[str] = None
    exception_resolved: bool = False
    matched_at: Optional[datetime] = None
    matched_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

