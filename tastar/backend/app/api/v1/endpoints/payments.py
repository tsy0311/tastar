"""
Payment Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Payment, PaymentAllocation, Invoice, User
from app.core.dependencies import get_current_active_user
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentAllocationCreate
from datetime import date

router = APIRouter()

@router.get("", response_model=List[PaymentResponse])
async def list_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    payment_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List payments"""
    query = db.query(Payment).filter(
        Payment.company_id == current_user.company_id
    )
    
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    
    if date_from:
        query = query.filter(Payment.payment_date >= date_from)
    
    if date_to:
        query = query.filter(Payment.payment_date <= date_to)
    
    payments = query.order_by(Payment.payment_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Build response with allocations
    result = []
    for payment in payments:
        allocations = db.query(PaymentAllocation).filter(
            PaymentAllocation.payment_id == payment.id
        ).all()
        
        result.append(
            PaymentResponse(
                id=str(payment.id),
                payment_number=payment.payment_number,
                payment_type=payment.payment_type,
                customer_id=str(payment.customer_id) if payment.customer_id else None,
                amount=payment.amount,
                payment_date=payment.payment_date,
                payment_method=payment.payment_method,
                payment_reference=payment.payment_reference,
                status=payment.status,
                currency_code=payment.currency_code,
                allocations=[
                    PaymentAllocationResponse(
                        id=str(alloc.id),
                        invoice_id=str(alloc.invoice_id) if alloc.invoice_id else None,
                        allocated_amount=alloc.allocated_amount,
                        allocation_date=alloc.allocation_date,
                    )
                    for alloc in allocations
                ],
                created_at=payment.created_at,
            )
        )
    
    return result

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment by ID"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.company_id == current_user.company_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Load allocations
    allocations = db.query(PaymentAllocation).filter(
        PaymentAllocation.payment_id == payment.id
    ).all()
    
    return PaymentResponse(
        id=str(payment.id),
        payment_number=payment.payment_number,
        payment_type=payment.payment_type,
        customer_id=str(payment.customer_id) if payment.customer_id else None,
        amount=payment.amount,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method,
        payment_reference=payment.payment_reference,
        status=payment.status,
        currency_code=payment.currency_code,
        allocations=[
            PaymentAllocationResponse(
                id=str(alloc.id),
                invoice_id=str(alloc.invoice_id) if alloc.invoice_id else None,
                allocated_amount=alloc.allocated_amount,
                allocation_date=alloc.allocation_date,
            )
            for alloc in allocations
        ],
        created_at=payment.created_at,
    )

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new payment"""
    # Generate payment number
    import re
    
    max_payment = db.query(Payment).filter(
        Payment.company_id == current_user.company_id,
        Payment.payment_number.like('PAY-%')
    ).order_by(Payment.payment_number.desc()).first()
    
    if max_payment:
        match = re.search(r'(\d+)$', max_payment.payment_number)
        max_num = int(match.group(1)) if match else 0
    else:
        max_num = 0
    
    payment_number = f"PAY-{str(max_num + 1).zfill(6)}"
    
    # Create payment
    payment = Payment(
        company_id=current_user.company_id,
        payment_number=payment_number,
        payment_type=payment_data.payment_type,
        customer_id=payment_data.customer_id,
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        payment_method=payment_data.payment_method,
        payment_reference=payment_data.payment_reference,
        status="completed",
        created_by=current_user.id,
    )
    
    db.add(payment)
    db.flush()
    
    # Create allocations if provided
    if payment_data.allocations:
        for allocation_data in payment_data.allocations:
            allocation = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=allocation_data.invoice_id,
                allocated_amount=allocation_data.amount,
                allocation_date=payment_data.payment_date,
            )
            db.add(allocation)
            
            # Update invoice balance
            invoice = db.query(Invoice).filter(Invoice.id == allocation_data.invoice_id).first()
            if invoice:
                invoice.paid_amount = (invoice.paid_amount or 0) + allocation_data.amount
                invoice.balance_amount = invoice.total_amount - invoice.paid_amount
                if invoice.balance_amount <= 0:
                    invoice.status = "paid"
    
    db.commit()
    db.refresh(payment)
    
    # Load allocations
    allocations = db.query(PaymentAllocation).filter(
        PaymentAllocation.payment_id == payment.id
    ).all()
    
    return PaymentResponse(
        id=str(payment.id),
        payment_number=payment.payment_number,
        payment_type=payment.payment_type,
        customer_id=str(payment.customer_id) if payment.customer_id else None,
        amount=payment.amount,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method,
        payment_reference=payment.payment_reference,
        status=payment.status,
        currency_code=payment.currency_code,
        allocations=[
            PaymentAllocationResponse(
                id=str(alloc.id),
                invoice_id=str(alloc.invoice_id) if alloc.invoice_id else None,
                allocated_amount=alloc.allocated_amount,
                allocation_date=alloc.allocation_date,
            )
            for alloc in allocations
        ],
        created_at=payment.created_at,
    )

