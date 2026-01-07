"""
CMS Endpoints for Field Management and AI Suggestions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database.connection import get_db
from app.database.cms_models import FieldDefinition, CustomFieldValue, AISuggestion, FieldType
from app.services.ai_suggestion_service import ai_suggestion_service
from app.core.dependencies import get_current_user
from app.database.models import User
from app.schemas.cms import (
    FieldDefinitionCreate,
    FieldDefinitionResponse,
    FieldDefinitionUpdate,
    AISuggestionRequest,
    AISuggestionResponse,
    AutofillRequest,
    AutofillResponse,
    CustomFieldValueCreate,
    CustomFieldValueResponse
)

router = APIRouter()

@router.get("/fields", response_model=List[FieldDefinitionResponse])
async def get_field_definitions(
    entity_type: str = Query(..., description="Entity type (company, customer, invoice, etc.)"),
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all field definitions for an entity type"""
    query = db.query(FieldDefinition).filter(
        FieldDefinition.entity_type == entity_type
    )
    
    # Filter by company or global fields
    if company_id:
        from uuid import UUID
        query = query.filter(
            (FieldDefinition.company_id == UUID(company_id)) | 
            (FieldDefinition.company_id.is_(None))
        )
    else:
        # Use current user's company
        query = query.filter(
            (FieldDefinition.company_id == current_user.company_id) | 
            (FieldDefinition.company_id.is_(None))
        )
    
    fields = query.order_by(FieldDefinition.field_order).all()
    
    return [
        {
            "id": str(f.id),
            "entity_type": f.entity_type,
            "field_key": f.field_key,
            "field_label": f.field_label,
            "field_type": f.field_type.value,
            "field_order": f.field_order,
            "is_required": f.is_required,
            "is_searchable": f.is_searchable,
            "is_visible": f.is_visible,
            "default_value": f.default_value,
            "options": f.options if f.options else None,
            "validation_rules": f.validation_rules,
            "ai_enabled": f.ai_enabled,
            "ai_context": f.ai_context
        }
        for f in fields
    ]

@router.post("/fields", response_model=FieldDefinitionResponse)
async def create_field_definition(
    field_data: FieldDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new field definition"""
    # Check if field_key already exists for this entity_type and company
    existing = db.query(FieldDefinition).filter(
        FieldDefinition.entity_type == field_data.entity_type,
        FieldDefinition.field_key == field_data.field_key,
        FieldDefinition.company_id == str(current_user.company_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Field key already exists")
    
    field_def = FieldDefinition(
        company_id=current_user.company_id,
        entity_type=field_data.entity_type,
        field_key=field_data.field_key,
        field_label=field_data.field_label,
        field_type=field_data.field_type,
        field_order=field_data.field_order,
        is_required=field_data.is_required,
        is_searchable=field_data.is_searchable,
        is_visible=field_data.is_visible,
        default_value=field_data.default_value,
        options=field_data.options,
        validation_rules=field_data.validation_rules,
        ai_enabled=field_data.ai_enabled,
        ai_context=field_data.ai_context
    )
    
    db.add(field_def)
    db.commit()
    db.refresh(field_def)
    
    return {
        "id": str(field_def.id),
        "entity_type": field_def.entity_type,
        "field_key": field_def.field_key,
        "field_label": field_def.field_label,
        "field_type": field_def.field_type.value,
        "field_order": field_def.field_order,
        "is_required": field_def.is_required,
        "is_searchable": field_def.is_searchable,
        "is_visible": field_def.is_visible,
        "default_value": field_def.default_value,
        "options": field_data.options,
        "validation_rules": field_data.validation_rules,
        "ai_enabled": field_def.ai_enabled,
        "ai_context": field_def.ai_context
    }

@router.post("/ai/suggest", response_model=AISuggestionResponse)
async def get_ai_suggestion(
    request: AISuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestion for a field"""
    # Get field definition
    field_def = db.query(FieldDefinition).filter(
        FieldDefinition.id == request.field_definition_id
    ).first()
    
    if not field_def:
        raise HTTPException(status_code=404, detail="Field definition not found")
    
    if not field_def.ai_enabled:
        return {
            "suggestion": "",
            "confidence": 0.0,
            "alternatives": []
        }
    
    # Generate suggestion
    suggestion_data = await ai_suggestion_service.generate_field_suggestion(
        field_label=field_def.field_label,
        field_type=field_def.field_type.value,
        partial_value=request.partial_value,
        context={"entity_type": request.entity_type, "ai_context": field_def.ai_context},
        existing_data=request.existing_data or {}
    )
    
    # Store suggestion for tracking
    if request.entity_id:
        suggestion = AISuggestion(
            field_definition_id=request.field_definition_id,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            suggested_value=suggestion_data["suggestion"],
            confidence_score=str(suggestion_data["confidence"]),
            suggestion_context=request.existing_data
        )
        db.add(suggestion)
        db.commit()
    
    return suggestion_data

@router.post("/ai/autofill", response_model=AutofillResponse)
async def autofill_entity(
    request: AutofillRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Autofill multiple fields for an entity"""
    # Get field definitions
    query = db.query(FieldDefinition).filter(
        FieldDefinition.entity_type == request.entity_type
    )
    
    # Filter by company or global
    query = query.filter(
        (FieldDefinition.company_id == str(current_user.company_id)) | 
        (FieldDefinition.company_id.is_(None))
    )
    
    if request.field_definition_ids:
        query = query.filter(FieldDefinition.id.in_(request.field_definition_ids))
    
    field_defs = query.all()
    
    # Convert to dict format
    field_def_dicts = [
        {
            "field_key": f.field_key,
            "field_label": f.field_label,
            "field_type": f.field_type.value
        }
        for f in field_defs
    ]
    
    # Generate autofill suggestions
    suggestions_dict = await ai_suggestion_service.autofill_entity(
        entity_type=request.entity_type,
        partial_data=request.partial_data,
        field_definitions=field_def_dicts
    )
    
    # Convert to response format
    suggestions_response = {}
    for field_key, suggestion_data in suggestions_dict.items():
        suggestions_response[field_key] = AISuggestionResponse(
            suggestion=suggestion_data.get("suggestion", ""),
            confidence=suggestion_data.get("confidence", 0.0),
            alternatives=suggestion_data.get("alternatives", [])
        )
    
    return AutofillResponse(suggestions=suggestions_response)

@router.get("/fields/{field_id}/values")
async def get_field_values(
    field_id: str,
    entity_type: str = Query(...),
    entity_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get custom field values for an entity"""
    query = db.query(CustomFieldValue).filter(
        CustomFieldValue.field_definition_id == field_id,
        CustomFieldValue.entity_type == entity_type
    )
    
    if entity_id:
        query = query.filter(CustomFieldValue.entity_id == entity_id)
    
    values = query.all()
    
    return [
        {
            "id": str(v.id),
            "field_definition_id": str(v.field_definition_id),
            "entity_type": v.entity_type,
            "entity_id": v.entity_id,
            "value": _get_value(v),
            "created_at": v.created_at.isoformat(),
            "updated_at": v.updated_at.isoformat()
        }
        for v in values
    ]

def _get_value(field_value: CustomFieldValue) -> Any:
    """Extract value from CustomFieldValue"""
    if field_value.value_text:
        return field_value.value_text
    elif field_value.value_number:
        return field_value.value_number
    elif field_value.value_boolean is not None:
        return field_value.value_boolean
    elif field_value.value_json:
        return field_value.value_json
    return None

