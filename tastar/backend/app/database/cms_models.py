"""
CMS Models for Flexible Field Management
Allows dynamic field definitions per company/customer
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid
import enum

class FieldType(str, enum.Enum):
    """Field data types"""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SELECT = "select"  # Dropdown with options
    MULTI_SELECT = "multi_select"
    TEXTAREA = "textarea"
    RICH_TEXT = "rich_text"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    URL = "url"

class FieldDefinition(Base):
    """Defines custom fields for entities"""
    __tablename__ = "field_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    
    # Entity type this field belongs to
    entity_type = Column(String(50), nullable=False)  # 'company', 'customer', 'invoice', etc.
    
    # Field properties
    field_key = Column(String(100), nullable=False)  # Internal key (e.g., 'custom_field_1')
    field_label = Column(String(255), nullable=False)  # Display label
    field_type = Column(SQLEnum(FieldType), nullable=False)
    field_order = Column(Integer, default=0)  # Display order
    
    # Field configuration
    is_required = Column(Boolean, default=False)
    is_searchable = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    default_value = Column(Text, nullable=True)
    
    # For select/multi_select fields
    options = Column(JSONB)  # Array of options: ["Option 1", "Option 2"]
    
    # Validation rules
    validation_rules = Column(JSONB)  # e.g., {"min": 0, "max": 100, "pattern": "regex"}
    
    # AI configuration
    ai_enabled = Column(Boolean, default=True)  # Enable AI suggestions for this field
    ai_context = Column(Text)  # Context for AI to generate better suggestions
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # Unique constraint: same field_key per entity_type per company
        # Allow null company_id for global fields
    )

class CustomFieldValue(Base):
    """Stores custom field values for entities"""
    __tablename__ = "custom_field_values"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_definition_id = Column(UUID(as_uuid=True), ForeignKey("field_definitions.id", ondelete="CASCADE"), nullable=False)
    
    # Entity reference (polymorphic)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)  # UUID of the entity
    
    # Value storage (flexible - can store any type)
    value_text = Column(Text, nullable=True)
    value_number = Column(String(50), nullable=True)  # Store as string for precision
    value_boolean = Column(Boolean, nullable=True)
    value_json = Column(JSONB, nullable=True)  # For complex values
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    field_definition = relationship("FieldDefinition")

class AISuggestion(Base):
    """Stores AI suggestions for fields"""
    __tablename__ = "ai_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_definition_id = Column(UUID(as_uuid=True), ForeignKey("field_definitions.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Suggestion data
    suggested_value = Column(Text, nullable=False)
    confidence_score = Column(String(10))  # 0.0 to 1.0
    suggestion_context = Column(JSONB)  # Context used to generate suggestion
    
    # Status
    is_accepted = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationship
    field_definition = relationship("FieldDefinition")

