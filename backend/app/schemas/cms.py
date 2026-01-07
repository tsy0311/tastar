"""
CMS Schemas for Field Definitions and Values
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FieldDefinitionBase(BaseModel):
    entity_type: str
    field_key: str
    field_label: str
    field_type: str
    field_order: int = 0
    is_required: bool = False
    is_searchable: bool = True
    is_visible: bool = True
    default_value: Optional[str] = None
    options: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    ai_enabled: bool = True
    ai_context: Optional[str] = None

class FieldDefinitionCreate(FieldDefinitionBase):
    pass

class FieldDefinitionUpdate(BaseModel):
    field_label: Optional[str] = None
    field_order: Optional[int] = None
    is_required: Optional[bool] = None
    is_searchable: Optional[bool] = None
    is_visible: Optional[bool] = None
    default_value: Optional[str] = None
    options: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    ai_enabled: Optional[bool] = None
    ai_context: Optional[str] = None

class FieldDefinitionResponse(FieldDefinitionBase):
    id: str
    company_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CustomFieldValueCreate(BaseModel):
    field_definition_id: str
    entity_type: str
    entity_id: str
    value: Any  # Can be string, number, boolean, or dict

class CustomFieldValueResponse(BaseModel):
    id: str
    field_definition_id: str
    entity_type: str
    entity_id: str
    value: Any
    created_at: datetime
    updated_at: datetime

class AISuggestionRequest(BaseModel):
    field_definition_id: str
    entity_type: str
    entity_id: Optional[str] = None
    partial_value: str = ""
    existing_data: Optional[Dict[str, Any]] = None

class AISuggestionResponse(BaseModel):
    suggestion: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: List[str] = []

class AutofillRequest(BaseModel):
    entity_type: str
    partial_data: Dict[str, Any]
    field_definition_ids: Optional[List[str]] = None

class AutofillResponse(BaseModel):
    suggestions: Dict[str, AISuggestionResponse]

