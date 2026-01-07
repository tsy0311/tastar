"""
User Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.database.models import User, Role, user_roles_table
from app.core.dependencies import get_current_active_user, require_role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.core.logging import logger

router = APIRouter()

@router.get("", response_model=List[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """List users"""
    query = db.query(User).filter(
        User.company_id == current_user.company_id,
        User.deleted_at.is_(None)
    )
    
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(User.status == status_filter)
    
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            status=user.status,
            roles=[role.name for role in user.roles],
            created_at=user.created_at,
        )
        for user in users
    ]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    # Users can only view their own profile unless they're admin
    if user_id != str(current_user.id) and "admin" not in [r.name for r in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        status=user.status,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create new user"""
    # Check if user already exists
    existing = db.query(User).filter(
        User.email == user_data.email.lower(),
        User.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    
    # Create user
    user = User(
        company_id=current_user.company_id,
        email=user_data.email.lower(),
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        status="active",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign roles if provided
    if user_data.roles:
        from sqlalchemy import insert
        for role_name in user_data.roles:
            role = db.query(Role).filter(
                Role.name == role_name,
                Role.company_id == current_user.company_id
            ).first()
            
            if role:
                stmt = insert(user_roles_table).values(
                    user_id=user.id,
                    role_id=role.id
                )
                db.execute(stmt)
    
    db.commit()
    
    # Reload user to get updated roles
    db.refresh(user)
    # Access roles to trigger lazy load
    _ = user.roles
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        status=user.status,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user"""
    # Users can only update their own profile unless they're admin
    if user_id != str(current_user.id) and "admin" not in [r.name for r in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Handle roles separately if provided
    if "roles" in update_data and "admin" in [r.name for r in current_user.roles]:
        from sqlalchemy import delete, insert
        
        # Remove existing roles
        db.execute(delete(user_roles_table).where(user_roles_table.c.user_id == user.id))
        
        # Add new roles
        for role_name in update_data["roles"]:
            role = db.query(Role).filter(
                Role.name == role_name,
                Role.company_id == current_user.company_id
            ).first()
            if role:
                db.execute(insert(user_roles_table).values(
                    user_id=user.id,
                    role_id=role.id
                ))
        
        # Remove roles from update_data
        del update_data["roles"]
    
    # Update other fields
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        status=user.status,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete user (soft delete)"""
    # Prevent self-deletion
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    from datetime import datetime
    user.deleted_at = datetime.utcnow()
    user.status = "inactive"
    
    db.commit()
    
    return {"success": True, "message": "User deleted successfully"}

