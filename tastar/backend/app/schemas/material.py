"""
Material Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class MaterialBase(BaseModel):
    material_code: str = Field(..., max_length=100)
    material_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    material_type: str = Field(..., description="raw, component, finished_good, consumable, tooling")
    unit_of_measure: str = Field(..., max_length=20)
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    reorder_point: Decimal = Decimal("0")
    reorder_quantity: Optional[Decimal] = None
    safety_stock: Decimal = Decimal("0")
    max_stock: Optional[Decimal] = None
    standard_cost: Optional[Decimal] = None
    preferred_supplier_id: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    material_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    material_type: Optional[str] = None
    unit_of_measure: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    standard_cost: Optional[Decimal] = None
    preferred_supplier_id: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class MaterialResponse(MaterialBase):
    id: str
    company_id: str
    current_stock: Decimal = Decimal("0")
    average_cost: Optional[Decimal] = None
    last_purchase_price: Optional[Decimal] = None
    status: str = "active"
    is_active: bool = True
    abc_category: Optional[str] = None
    turnover_rate: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

