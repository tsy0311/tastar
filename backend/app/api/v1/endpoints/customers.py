"""
Customer Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.connection import get_db
from app.database.models import Customer, User
from app.core.dependencies import get_current_active_user
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()

@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List customers"""
    query = db.query(Customer).filter(
        Customer.company_id == current_user.company_id,
        Customer.deleted_at.is_(None)
    )
    
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.primary_email.ilike(f"%{search}%")
            )
        )
    
    if status_filter:
        query = query.filter(Customer.status == status_filter)
    
    total = query.count()
    customers = query.offset((page - 1) * limit).limit(limit).all()
    
    return [
        CustomerResponse(
            id=str(c.id),
            customer_code=c.customer_code,
            name=c.name,
            legal_name=c.legal_name,
            tax_id=c.tax_id,
            customer_type=c.customer_type,
            industry=c.industry,
            segment=c.segment,
            primary_email=c.primary_email,
            primary_phone=c.primary_phone,
            credit_limit=c.credit_limit,
            payment_terms=c.payment_terms,
            currency_code=c.currency_code,
            status=c.status,
            created_at=c.created_at,
        )
        for c in customers
    ]

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get customer by ID"""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.company_id == current_user.company_id,
        Customer.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    return CustomerResponse(
        id=str(customer.id),
        customer_code=customer.customer_code,
        name=customer.name,
        legal_name=customer.legal_name,
        tax_id=customer.tax_id,
        customer_type=customer.customer_type,
        industry=customer.industry,
        segment=customer.segment,
        primary_email=customer.primary_email,
        primary_phone=customer.primary_phone,
        credit_limit=customer.credit_limit,
        payment_terms=customer.payment_terms,
        currency_code=customer.currency_code,
        status=customer.status,
        created_at=customer.created_at,
    )

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new customer"""
    # Check if customer code already exists
    existing = db.query(Customer).filter(
        Customer.company_id == current_user.company_id,
        Customer.customer_code == customer_data.customer_code,
        Customer.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this code already exists",
        )
    
    # Create customer
    customer = Customer(
        company_id=current_user.company_id,
        **customer_data.model_dump()
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse(
        id=str(customer.id),
        customer_code=customer.customer_code,
        name=customer.name,
        legal_name=customer.legal_name,
        tax_id=customer.tax_id,
        customer_type=customer.customer_type,
        industry=customer.industry,
        segment=customer.segment,
        primary_email=customer.primary_email,
        primary_phone=customer.primary_phone,
        credit_limit=customer.credit_limit,
        payment_terms=customer.payment_terms,
        currency_code=customer.currency_code,
        status=customer.status,
        created_at=customer.created_at,
    )

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update customer"""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.company_id == current_user.company_id,
        Customer.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    # Update fields
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse(
        id=str(customer.id),
        customer_code=customer.customer_code,
        name=customer.name,
        legal_name=customer.legal_name,
        tax_id=customer.tax_id,
        customer_type=customer.customer_type,
        industry=customer.industry,
        segment=customer.segment,
        primary_email=customer.primary_email,
        primary_phone=customer.primary_phone,
        credit_limit=customer.credit_limit,
        payment_terms=customer.payment_terms,
        currency_code=customer.currency_code,
        status=customer.status,
        created_at=customer.created_at,
    )

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete customer (soft delete)"""
    from datetime import datetime
    
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.company_id == current_user.company_id,
        Customer.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    customer.deleted_at = datetime.utcnow()
    customer.status = "inactive"
    
    db.commit()
    
    return {"success": True, "message": "Customer deleted successfully"}

