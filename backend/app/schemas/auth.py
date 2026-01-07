"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str

class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    first_name: str
    last_name: str
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token response schema"""
    token: str
    refresh_token: Optional[str] = None
    expires_in: int
    user: Optional[UserResponse] = None

