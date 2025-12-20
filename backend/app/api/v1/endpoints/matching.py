"""
Transaction Matching Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal
import uuid

from app.database.connection import get_db
from app.database.models import TransactionMatching, User, PurchaseOrder, Invoice, Bill
from app.core.dependencies import get_current_active_user
from app.schemas.matching import TransactionMatchingCreate, TransactionMatchingResponse

router = APIRouter()

@router.post("", response_model=TransactionMatchingResponse)
async def create_match(
    match_data: TransactionMatchingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create transaction match (two-way or three-way)"""
    # Validate at least two references are provided
    refs = [
        match_data.purchase_order_id,
        match_data.delivery_order_id,
        match_data.invoice_id,
        match_data.bill_id
    ]
    provided_refs = [r for r in refs if r]
    
    if len(provided_refs) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two references (PO, DO, Invoice, Bill) are required for matching"
        )
    
    # Validate match type
    if match_data.match_type == "three_way" and len(provided_refs) < 3:
        raise HTTPException(
            status_code=400,
            detail="Three-way matching requires at least three references"
        )
    
    # Validate references exist and belong to company
    po = None
    invoice = None
    bill = None
    
    if match_data.purchase_order_id:
        try:
            po = db.query(PurchaseOrder).filter(
                PurchaseOrder.id == uuid.UUID(match_data.purchase_order_id),
                PurchaseOrder.company_id == current_user.company_id
            ).first()
            if not po:
                raise HTTPException(status_code=404, detail="Purchase order not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid purchase order ID format")
    
    if match_data.invoice_id:
        try:
            invoice = db.query(Invoice).filter(
                Invoice.id == uuid.UUID(match_data.invoice_id),
                Invoice.company_id == current_user.company_id
            ).first()
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid invoice ID format")
    
    if match_data.bill_id:
        try:
            bill = db.query(Bill).filter(
                Bill.id == uuid.UUID(match_data.bill_id),
                Bill.company_id == current_user.company_id
            ).first()
            if not bill:
                raise HTTPException(status_code=404, detail="Bill not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bill ID format")
    
    # Perform matching logic
    amount_variance = None
    within_tolerance = None
    match_status = "pending"
    confidence_score = Decimal("0")
    
    if po and bill:
        # Match PO to Bill
        amount_variance = abs(po.total_amount - bill.total_amount)
        tolerance = match_data.tolerance_threshold or Decimal("0.01")  # 1 cent default
        within_tolerance = amount_variance <= tolerance
        
        if within_tolerance:
            match_status = "matched"
            confidence_score = Decimal("0.95")
        else:
            match_status = "exception"
            confidence_score = Decimal("0.50")
    
    elif po and invoice:
        # Match PO to Invoice (for sales)
        amount_variance = abs(po.total_amount - invoice.total_amount)
        tolerance = match_data.tolerance_threshold or Decimal("0.01")
        within_tolerance = amount_variance <= tolerance
        
        if within_tolerance:
            match_status = "matched"
            confidence_score = Decimal("0.95")
        else:
            match_status = "exception"
            confidence_score = Decimal("0.50")
    
    # Create match record
    match = TransactionMatching(
        company_id=current_user.company_id,
        purchase_order_id=uuid.UUID(match_data.purchase_order_id) if match_data.purchase_order_id else None,
        invoice_id=uuid.UUID(match_data.invoice_id) if match_data.invoice_id else None,
        bill_id=uuid.UUID(match_data.bill_id) if match_data.bill_id else None,
        match_type=match_data.match_type,
        match_status=match_status,
        match_confidence_score=confidence_score,
        amount_variance=amount_variance,
        tolerance_threshold=match_data.tolerance_threshold or Decimal("0.01"),
        within_tolerance=within_tolerance,
        exception_reason=f"Amount variance: {amount_variance}" if amount_variance and not within_tolerance else None,
        matched_by=current_user.id if match_status == "matched" else None,
        matched_at=datetime.utcnow() if match_status == "matched" else None,
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return TransactionMatchingResponse(
        id=str(match.id),
        company_id=str(match.company_id),
        purchase_order_id=str(match.purchase_order_id) if match.purchase_order_id else None,
        delivery_order_id=str(match.delivery_order_id) if match.delivery_order_id else None,
        invoice_id=str(match.invoice_id) if match.invoice_id else None,
        bill_id=str(match.bill_id) if match.bill_id else None,
        match_type=match.match_type,
        match_status=match.match_status,
        match_confidence_score=match.match_confidence_score,
        amount_variance=match.amount_variance,
        quantity_variance=match.quantity_variance,
        date_variance=match.date_variance,
        tolerance_threshold=match.tolerance_threshold,
        within_tolerance=match.within_tolerance,
        exception_reason=match.exception_reason,
        exception_resolved=match.exception_resolved,
        matched_at=match.matched_at,
        matched_by=str(match.matched_by) if match.matched_by else None,
        created_at=match.created_at,
        updated_at=match.updated_at,
    )

@router.get("", response_model=List[TransactionMatchingResponse])
async def list_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    match_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List transaction matches"""
    query = db.query(TransactionMatching).filter(
        TransactionMatching.company_id == current_user.company_id
    )
    
    if status_filter:
        query = query.filter(TransactionMatching.match_status == status_filter)
    
    if match_type:
        query = query.filter(TransactionMatching.match_type == match_type)
    
    matches = query.order_by(TransactionMatching.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return [
        TransactionMatchingResponse(
            id=str(match.id),
            company_id=str(match.company_id),
            purchase_order_id=str(match.purchase_order_id) if match.purchase_order_id else None,
            delivery_order_id=str(match.delivery_order_id) if match.delivery_order_id else None,
            invoice_id=str(match.invoice_id) if match.invoice_id else None,
            bill_id=str(match.bill_id) if match.bill_id else None,
            match_type=match.match_type,
            match_status=match.match_status,
            match_confidence_score=match.match_confidence_score,
            amount_variance=match.amount_variance,
            quantity_variance=match.quantity_variance,
            date_variance=match.date_variance,
            tolerance_threshold=match.tolerance_threshold,
            within_tolerance=match.within_tolerance,
            exception_reason=match.exception_reason,
            exception_resolved=match.exception_resolved,
            matched_at=match.matched_at,
            matched_by=str(match.matched_by) if match.matched_by else None,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )
        for match in matches
    ]

@router.get("/exceptions", response_model=List[TransactionMatchingResponse])
async def get_exceptions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    unresolved_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get matching exceptions"""
    query = db.query(TransactionMatching).filter(
        TransactionMatching.company_id == current_user.company_id,
        TransactionMatching.match_status == "exception"
    )
    
    if unresolved_only:
        query = query.filter(TransactionMatching.exception_resolved == False)
    
    exceptions = query.order_by(TransactionMatching.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return [
        TransactionMatchingResponse(
            id=str(match.id),
            company_id=str(match.company_id),
            purchase_order_id=str(match.purchase_order_id) if match.purchase_order_id else None,
            delivery_order_id=str(match.delivery_order_id) if match.delivery_order_id else None,
            invoice_id=str(match.invoice_id) if match.invoice_id else None,
            bill_id=str(match.bill_id) if match.bill_id else None,
            match_type=match.match_type,
            match_status=match.match_status,
            match_confidence_score=match.match_confidence_score,
            amount_variance=match.amount_variance,
            quantity_variance=match.quantity_variance,
            date_variance=match.date_variance,
            tolerance_threshold=match.tolerance_threshold,
            within_tolerance=match.within_tolerance,
            exception_reason=match.exception_reason,
            exception_resolved=match.exception_resolved,
            matched_at=match.matched_at,
            matched_by=str(match.matched_by) if match.matched_by else None,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )
        for match in exceptions
    ]

@router.post("/{match_id}/resolve", response_model=TransactionMatchingResponse)
async def resolve_exception(
    match_id: str,
    resolution_note: str = Body(..., embed=True, description="Resolution note"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resolve matching exception"""
    try:
        match = db.query(TransactionMatching).filter(
            TransactionMatching.id == uuid.UUID(match_id),
            TransactionMatching.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid match ID format")
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.match_status != "exception":
        raise HTTPException(status_code=400, detail="Only exceptions can be resolved")
    
    match.exception_resolved = True
    match.match_status = "resolved"
    if match.exception_reason:
        match.exception_reason = f"{match.exception_reason} | Resolved: {resolution_note}"
    else:
        match.exception_reason = f"Resolved: {resolution_note}"
    
    db.commit()
    db.refresh(match)
    
    return TransactionMatchingResponse(
        id=str(match.id),
        company_id=str(match.company_id),
        purchase_order_id=str(match.purchase_order_id) if match.purchase_order_id else None,
        delivery_order_id=str(match.delivery_order_id) if match.delivery_order_id else None,
        invoice_id=str(match.invoice_id) if match.invoice_id else None,
        bill_id=str(match.bill_id) if match.bill_id else None,
        match_type=match.match_type,
        match_status=match.match_status,
        match_confidence_score=match.match_confidence_score,
        amount_variance=match.amount_variance,
        quantity_variance=match.quantity_variance,
        date_variance=match.date_variance,
        tolerance_threshold=match.tolerance_threshold,
        within_tolerance=match.within_tolerance,
        exception_reason=match.exception_reason,
        exception_resolved=match.exception_resolved,
        matched_at=match.matched_at,
        matched_by=str(match.matched_by) if match.matched_by else None,
        created_at=match.created_at,
        updated_at=match.updated_at,
    )

