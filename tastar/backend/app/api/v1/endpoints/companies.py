"""
Company Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database.models import Company, User
from app.core.dependencies import get_current_active_user, require_role
from app.schemas.company import CompanyUpdate, CompanyResponse

router = APIRouter()

@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List companies - users can only see their own company"""
    company = db.query(Company).filter(
        Company.id == current_user.company_id,
        Company.deleted_at.is_(None)
    ).first()
    
    if not company:
        # Return empty list if company not found
        return []
    
    return [
        CompanyResponse(
            id=str(company.id),
            name=company.name,
            legal_name=company.legal_name,
            tax_id=company.tax_id,
            country=company.country,
            currency_code=company.currency_code,
            timezone=company.timezone,
            locale=company.locale,
            created_at=company.created_at,
        )
    ]

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get company by ID"""
    # Users can only view their own company
    if company_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.deleted_at.is_(None)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        legal_name=company.legal_name,
        tax_id=company.tax_id,
        country=company.country,
        currency_code=company.currency_code,
        timezone=company.timezone,
        locale=company.locale,
        created_at=company.created_at,
    )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update company"""
    # Users can only update their own company
    if company_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.deleted_at.is_(None)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    
    # Update fields
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    return CompanyResponse(
        id=str(company.id),
        name=company.name,
        legal_name=company.legal_name,
        tax_id=company.tax_id,
        country=company.country,
        currency_code=company.currency_code,
        timezone=company.timezone,
        locale=company.locale,
        created_at=company.created_at,
    )

