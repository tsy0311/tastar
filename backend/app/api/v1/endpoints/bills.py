"""
Bill (Accounts Payable) Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import date, datetime
from decimal import Decimal
import uuid

from app.database.connection import get_db
from app.database.models import Bill, User, Supplier, PurchaseOrder
from app.core.dependencies import get_current_active_user, require_role
from app.schemas.bill import BillCreate, BillUpdate, BillResponse

router = APIRouter()

@router.get("", response_model=List[BillResponse])
async def list_bills(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    supplier_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    overdue_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List bills with filters"""
    query = db.query(Bill).filter(
        Bill.company_id == current_user.company_id
    )
    
    if search:
        query = query.filter(
            or_(
                Bill.bill_number.ilike(f"%{search}%"),
                Bill.vendor_invoice_number.ilike(f"%{search}%"),
                Bill.notes.ilike(f"%{search}%")
            )
        )
    
    if supplier_id:
        try:
            query = query.filter(Bill.supplier_id == uuid.UUID(supplier_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid supplier ID format")
    
    if status_filter:
        query = query.filter(Bill.status == status_filter)
    
    if date_from:
        query = query.filter(Bill.bill_date >= date_from)
    
    if date_to:
        query = query.filter(Bill.bill_date <= date_to)
    
    if overdue_only:
        query = query.filter(
            Bill.status != "paid",
            Bill.due_date < date.today()
        )
    
    bills = query.order_by(Bill.bill_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return [
        BillResponse(
            id=str(bill.id),
            company_id=str(bill.company_id),
            bill_number=bill.bill_number,
            vendor_invoice_number=bill.vendor_invoice_number,
            supplier_id=str(bill.supplier_id),
            purchase_order_id=str(bill.purchase_order_id) if bill.purchase_order_id else None,
            bill_date=bill.bill_date,
            due_date=bill.due_date,
            subtotal=bill.subtotal,
            tax_amount=bill.tax_amount,
            discount_amount=bill.discount_amount,
            total_amount=bill.total_amount,
            paid_amount=bill.paid_amount,
            balance_amount=bill.balance_amount,
            currency_code=bill.currency_code,
            status=bill.status,
            approval_status=bill.approval_status,
            notes=bill.notes,
            attachment_url=bill.attachment_url,
            created_by=str(bill.created_by) if bill.created_by else None,
            created_at=bill.created_at,
            updated_at=bill.updated_at,
        )
        for bill in bills
    ]

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get bill by ID"""
    try:
        bill = db.query(Bill).filter(
            Bill.id == uuid.UUID(bill_id),
            Bill.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bill ID format")
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return BillResponse(
        id=str(bill.id),
        company_id=str(bill.company_id),
        bill_number=bill.bill_number,
        vendor_invoice_number=bill.vendor_invoice_number,
        supplier_id=str(bill.supplier_id),
        purchase_order_id=str(bill.purchase_order_id) if bill.purchase_order_id else None,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        subtotal=bill.subtotal,
        tax_amount=bill.tax_amount,
        discount_amount=bill.discount_amount,
        total_amount=bill.total_amount,
        paid_amount=bill.paid_amount,
        balance_amount=bill.balance_amount,
        currency_code=bill.currency_code,
        status=bill.status,
        approval_status=bill.approval_status,
        notes=bill.notes,
        attachment_url=bill.attachment_url,
        created_by=str(bill.created_by) if bill.created_by else None,
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )

@router.post("", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new bill"""
    # Validate supplier exists
    try:
        supplier = db.query(Supplier).filter(
            Supplier.id == uuid.UUID(bill_data.supplier_id),
            Supplier.company_id == current_user.company_id,
            Supplier.deleted_at.is_(None)
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid supplier ID format")
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Validate PO if provided
    if bill_data.purchase_order_id:
        try:
            po = db.query(PurchaseOrder).filter(
                PurchaseOrder.id == uuid.UUID(bill_data.purchase_order_id),
                PurchaseOrder.company_id == current_user.company_id
            ).first()
            if not po:
                raise HTTPException(status_code=404, detail="Purchase order not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid purchase order ID format")
    
    # Check if bill number already exists
    existing = db.query(Bill).filter(
        Bill.company_id == current_user.company_id,
        Bill.bill_number == bill_data.bill_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Bill number already exists")
    
    # Create bill
    bill = Bill(
        company_id=current_user.company_id,
        supplier_id=uuid.UUID(bill_data.supplier_id),
        purchase_order_id=uuid.UUID(bill_data.purchase_order_id) if bill_data.purchase_order_id else None,
        bill_number=bill_data.bill_number,
        vendor_invoice_number=bill_data.vendor_invoice_number,
        bill_date=bill_data.bill_date,
        due_date=bill_data.due_date,
        subtotal=bill_data.subtotal,
        tax_amount=bill_data.tax_amount,
        discount_amount=bill_data.discount_amount,
        total_amount=bill_data.total_amount,
        balance_amount=bill_data.total_amount,
        currency_code=bill_data.currency_code,
        notes=bill_data.notes,
        attachment_url=bill_data.attachment_url,
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(bill)
    db.commit()
    db.refresh(bill)
    
    return BillResponse(
        id=str(bill.id),
        company_id=str(bill.company_id),
        bill_number=bill.bill_number,
        vendor_invoice_number=bill.vendor_invoice_number,
        supplier_id=str(bill.supplier_id),
        purchase_order_id=str(bill.purchase_order_id) if bill.purchase_order_id else None,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        subtotal=bill.subtotal,
        tax_amount=bill.tax_amount,
        discount_amount=bill.discount_amount,
        total_amount=bill.total_amount,
        paid_amount=bill.paid_amount,
        balance_amount=bill.balance_amount,
        currency_code=bill.currency_code,
        status=bill.status,
        approval_status=bill.approval_status,
        notes=bill.notes,
        attachment_url=bill.attachment_url,
        created_by=str(bill.created_by) if bill.created_by else None,
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )

@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: str,
    bill_data: BillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update bill"""
    try:
        bill = db.query(Bill).filter(
            Bill.id == uuid.UUID(bill_id),
            Bill.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bill ID format")
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    if bill.status in ['paid', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update bill with status: {bill.status}"
        )
    
    update_data = bill_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bill, field, value)
    
    db.commit()
    db.refresh(bill)
    
    return BillResponse(
        id=str(bill.id),
        company_id=str(bill.company_id),
        bill_number=bill.bill_number,
        vendor_invoice_number=bill.vendor_invoice_number,
        supplier_id=str(bill.supplier_id),
        purchase_order_id=str(bill.purchase_order_id) if bill.purchase_order_id else None,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        subtotal=bill.subtotal,
        tax_amount=bill.tax_amount,
        discount_amount=bill.discount_amount,
        total_amount=bill.total_amount,
        paid_amount=bill.paid_amount,
        balance_amount=bill.balance_amount,
        currency_code=bill.currency_code,
        status=bill.status,
        approval_status=bill.approval_status,
        notes=bill.notes,
        attachment_url=bill.attachment_url,
        created_by=str(bill.created_by) if bill.created_by else None,
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )

@router.post("/{bill_id}/approve", response_model=BillResponse)
async def approve_bill(
    bill_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve bill"""
    try:
        bill = db.query(Bill).filter(
            Bill.id == uuid.UUID(bill_id),
            Bill.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bill ID format")
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    if bill.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft bills can be approved")
    
    bill.approval_status = "approved"
    bill.status = "pending"  # Ready for payment
    
    db.commit()
    db.refresh(bill)
    
    return BillResponse(
        id=str(bill.id),
        company_id=str(bill.company_id),
        bill_number=bill.bill_number,
        vendor_invoice_number=bill.vendor_invoice_number,
        supplier_id=str(bill.supplier_id),
        purchase_order_id=str(bill.purchase_order_id) if bill.purchase_order_id else None,
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        subtotal=bill.subtotal,
        tax_amount=bill.tax_amount,
        discount_amount=bill.discount_amount,
        total_amount=bill.total_amount,
        paid_amount=bill.paid_amount,
        balance_amount=bill.balance_amount,
        currency_code=bill.currency_code,
        status=bill.status,
        approval_status=bill.approval_status,
        notes=bill.notes,
        attachment_url=bill.attachment_url,
        created_by=str(bill.created_by) if bill.created_by else None,
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )

@router.get("/aging", response_model=dict)
async def get_aging_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get accounts payable aging report"""
    today = date.today()
    
    # Get all unpaid bills
    bills = db.query(Bill).filter(
        Bill.company_id == current_user.company_id,
        Bill.status.in_(['draft', 'pending', 'approved', 'partial']),
        Bill.balance_amount > 0
    ).all()
    
    # Calculate aging buckets
    current = Decimal("0")
    days_30 = Decimal("0")
    days_60 = Decimal("0")
    days_90 = Decimal("0")
    days_90_plus = Decimal("0")
    
    aging_details = []
    
    for bill in bills:
        days_overdue = (today - bill.due_date).days if bill.due_date < today else 0
        
        if days_overdue <= 0:
            bucket = "current"
            current += bill.balance_amount
        elif days_overdue <= 30:
            bucket = "1-30"
            days_30 += bill.balance_amount
        elif days_overdue <= 60:
            bucket = "31-60"
            days_60 += bill.balance_amount
        elif days_overdue <= 90:
            bucket = "61-90"
            days_90 += bill.balance_amount
        else:
            bucket = "90+"
            days_90_plus += bill.balance_amount
        
        aging_details.append({
            "bill_id": str(bill.id),
            "bill_number": bill.bill_number,
            "supplier_id": str(bill.supplier_id),
            "due_date": bill.due_date.isoformat(),
            "days_overdue": days_overdue,
            "balance_amount": float(bill.balance_amount),
            "aging_bucket": bucket
        })
    
    total = current + days_30 + days_60 + days_90 + days_90_plus
    
    return {
        "success": True,
        "report_date": today.isoformat(),
        "summary": {
            "current": float(current),
            "1_30_days": float(days_30),
            "31_60_days": float(days_60),
            "61_90_days": float(days_90),
            "90_plus_days": float(days_90_plus),
            "total": float(total)
        },
        "details": aging_details
    }

