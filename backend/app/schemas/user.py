"""
User Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema"""
    password: str
    roles: Optional[List[str]] = []

class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    status: Optional[str] = None
    roles: Optional[List[str]] = None

class UserResponse(UserBase):
    """User response schema"""
    id: str
    status: str
    roles: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

