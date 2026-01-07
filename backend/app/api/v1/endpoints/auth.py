"""
Authentication Endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.core.security import verify_password, create_access_token, create_refresh_token, get_password_hash, decode_token
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse
from app.core.logging import logger

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    # Find user by email
    user = db.query(User).filter(
        User.email == login_data.email.lower(),
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = create_access_token(
        data={
            "userId": str(user.id),
            "email": user.email,
            "companyId": str(user.company_id),
        }
    )
    
    refresh_token = create_refresh_token(
        data={"userId": str(user.id)}
    )
    
    return TokenResponse(
        token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=[role.name for role in user.roles],
        )
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        user_id = payload.get("userId") or payload.get("user_id")
        user = db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Generate new access token
        access_token = create_access_token(
            data={
                "userId": str(user.id),
                "email": user.email,
                "companyId": str(user.company_id),
            }
        )
        
        return TokenResponse(
            token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user (token blacklisting would be implemented here)"""
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        roles=[role.name for role in current_user.roles],
    )

