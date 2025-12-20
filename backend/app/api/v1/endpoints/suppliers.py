"""
Supplier Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.database.models import Supplier, User
from app.core.dependencies import get_current_active_user
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter()

@router.get("", response_model=List[SupplierResponse])
async def list_suppliers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List suppliers"""
    query = db.query(Supplier).filter(
        Supplier.company_id == current_user.company_id,
        Supplier.deleted_at.is_(None)
    )
    
    if search:
        query = query.filter(
            or_(
                Supplier.name.ilike(f"%{search}%"),
                Supplier.supplier_code.ilike(f"%{search}%"),
                Supplier.primary_email.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(Supplier.status == status_filter)
    
    suppliers = query.offset((page - 1) * limit).limit(limit).all()
    
    return [
        SupplierResponse(
            id=str(s.id),
            company_id=str(s.company_id),
            supplier_code=s.supplier_code,
            name=s.name,
            legal_name=s.legal_name,
            tax_id=s.tax_id,
            address_line1=s.address_line1,
            address_line2=s.address_line2,
            city=s.city,
            state=s.state,
            postal_code=s.postal_code,
            country=s.country,
            primary_contact_name=s.primary_contact_name,
            primary_email=s.primary_email,
            primary_phone=s.primary_phone,
            website=s.website,
            payment_terms=s.payment_terms,
            currency_code=s.currency_code,
            credit_limit=s.credit_limit,
            on_time_delivery_rate=s.on_time_delivery_rate,
            quality_score=s.quality_score,
            average_rating=s.average_rating,
            total_orders=s.total_orders,
            total_spent=s.total_spent,
            status=s.status,
            risk_score=s.risk_score,
            risk_level=s.risk_level,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in suppliers
    ]

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get supplier by ID"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.company_id == current_user.company_id,
        Supplier.deleted_at.is_(None)
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return SupplierResponse(
        id=str(supplier.id),
        company_id=str(supplier.company_id),
        supplier_code=supplier.supplier_code,
        name=supplier.name,
        legal_name=supplier.legal_name,
        tax_id=supplier.tax_id,
        address_line1=supplier.address_line1,
        address_line2=supplier.address_line2,
        city=supplier.city,
        state=supplier.state,
        postal_code=supplier.postal_code,
        country=supplier.country,
        primary_contact_name=supplier.primary_contact_name,
        primary_email=supplier.primary_email,
        primary_phone=supplier.primary_phone,
        website=supplier.website,
        payment_terms=supplier.payment_terms,
        currency_code=supplier.currency_code,
        credit_limit=supplier.credit_limit,
        on_time_delivery_rate=supplier.on_time_delivery_rate,
        quality_score=supplier.quality_score,
        average_rating=supplier.average_rating,
        total_orders=supplier.total_orders,
        total_spent=supplier.total_spent,
        status=supplier.status,
        risk_score=supplier.risk_score,
        risk_level=supplier.risk_level,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    )

@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new supplier"""
    # Check if supplier code already exists
    existing = db.query(Supplier).filter(
        Supplier.company_id == current_user.company_id,
        Supplier.supplier_code == supplier_data.supplier_code,
        Supplier.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    
    supplier = Supplier(
        company_id=current_user.company_id,
        **supplier_data.model_dump()
    )
    
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    return SupplierResponse(
        id=str(supplier.id),
        company_id=str(supplier.company_id),
        **supplier_data.model_dump(),
        on_time_delivery_rate=None,
        quality_score=None,
        average_rating=None,
        total_orders=0,
        total_spent=0,
        status="active",
        risk_score=None,
        risk_level=None,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    )

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update supplier"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.company_id == current_user.company_id,
        Supplier.deleted_at.is_(None)
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    update_data = supplier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    return SupplierResponse(
        id=str(supplier.id),
        company_id=str(supplier.company_id),
        supplier_code=supplier.supplier_code,
        name=supplier.name,
        legal_name=supplier.legal_name,
        tax_id=supplier.tax_id,
        address_line1=supplier.address_line1,
        address_line2=supplier.address_line2,
        city=supplier.city,
        state=supplier.state,
        postal_code=supplier.postal_code,
        country=supplier.country,
        primary_contact_name=supplier.primary_contact_name,
        primary_email=supplier.primary_email,
        primary_phone=supplier.primary_phone,
        website=supplier.website,
        payment_terms=supplier.payment_terms,
        currency_code=supplier.currency_code,
        credit_limit=supplier.credit_limit,
        on_time_delivery_rate=supplier.on_time_delivery_rate,
        quality_score=supplier.quality_score,
        average_rating=supplier.average_rating,
        total_orders=supplier.total_orders,
        total_spent=supplier.total_spent,
        status=supplier.status,
        risk_score=supplier.risk_score,
        risk_level=supplier.risk_level,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    )

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete supplier (soft delete)"""
    from datetime import datetime
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.company_id == current_user.company_id,
        Supplier.deleted_at.is_(None)
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier.deleted_at = datetime.utcnow()
    db.commit()
    
    return None

