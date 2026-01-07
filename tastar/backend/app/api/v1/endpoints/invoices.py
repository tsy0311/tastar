"""
Invoice Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Invoice, InvoiceLineItem, Customer, User
from app.core.dependencies import get_current_active_user
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceLineItemCreate, InvoiceLineItemResponse
from datetime import datetime, date

router = APIRouter()

@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    customer_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    overdue_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List invoices"""
    query = db.query(Invoice).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None)
    )
    
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    if date_from:
        query = query.filter(Invoice.invoice_date >= date_from)
    
    if date_to:
        query = query.filter(Invoice.invoice_date <= date_to)
    
    if overdue_only:
        query = query.filter(
            Invoice.status != "paid",
            Invoice.due_date < date.today()
        )
    
    invoices = query.order_by(Invoice.invoice_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Build response with line items
    result = []
    for invoice in invoices:
        line_items = db.query(InvoiceLineItem).filter(
            InvoiceLineItem.invoice_id == invoice.id
        ).order_by(InvoiceLineItem.line_number).all()
        
        result.append(
            InvoiceResponse(
                id=str(invoice.id),
                customer_id=str(invoice.customer_id),
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date,
                due_date=invoice.due_date,
                payment_terms=invoice.payment_terms,
                notes=invoice.notes,
                subtotal=invoice.subtotal,
                tax_amount=invoice.tax_amount,
                total_amount=invoice.total_amount,
                paid_amount=invoice.paid_amount,
                balance_amount=invoice.balance_amount,
                status=invoice.status,
                currency_code=invoice.currency_code,
                line_items=[
                    InvoiceLineItemResponse(
                        id=str(item.id),
                        line_number=item.line_number,
                        description=item.description,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        discount_percent=item.discount_percent,
                        tax_rate=item.tax_rate,
                        line_total=item.line_total,
                        tax_amount=item.tax_amount,
                    )
                    for item in line_items
                ],
                created_at=invoice.created_at,
            )
        )
    
    return result

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    # Load line items
    line_items = db.query(InvoiceLineItem).filter(
        InvoiceLineItem.invoice_id == invoice.id
    ).order_by(InvoiceLineItem.line_number).all()
    
    return InvoiceResponse(
        id=str(invoice.id),
        customer_id=str(invoice.customer_id),
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        payment_terms=invoice.payment_terms,
        notes=invoice.notes,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
        paid_amount=invoice.paid_amount,
        balance_amount=invoice.balance_amount,
        status=invoice.status,
        currency_code=invoice.currency_code,
        line_items=[
            InvoiceLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
            )
            for item in line_items
        ],
        created_at=invoice.created_at,
    )

@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new invoice"""
    # Verify customer exists
    customer = db.query(Customer).filter(
        Customer.id == invoice_data.customer_id,
        Customer.company_id == current_user.company_id,
        Customer.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    
    # Generate invoice number
    from sqlalchemy import cast, Integer
    from sqlalchemy.dialects.postgresql import REGEXP_REPLACE
    
    # Get max invoice number
    max_invoice = db.query(Invoice).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_number.like('INV-%')
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if max_invoice:
        # Extract number from invoice_number (e.g., "INV-000123" -> 123)
        import re
        match = re.search(r'(\d+)$', max_invoice.invoice_number)
        max_num = int(match.group(1)) if match else 0
    else:
        max_num = 0
    
    invoice_number = f"INV-{str(max_num + 1).zfill(6)}"
    
    # Calculate totals
    subtotal = sum(
        item.quantity * item.unit_price * (1 - (item.discount_percent or 0) / 100)
        for item in invoice_data.line_items
    )
    tax_amount = sum(
        item.quantity * item.unit_price * (1 - (item.discount_percent or 0) / 100) * (item.tax_rate or 0)
        for item in invoice_data.line_items
    )
    total_amount = subtotal + tax_amount
    
    # Create invoice
    invoice = Invoice(
        company_id=current_user.company_id,
        customer_id=invoice_data.customer_id,
        invoice_number=invoice_number,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        balance_amount=total_amount,
        payment_terms=invoice_data.payment_terms,
        notes=invoice_data.notes,
        created_by=current_user.id,
    )
    
    db.add(invoice)
    db.flush()
    
    # Create line items
    for idx, item_data in enumerate(invoice_data.line_items, 1):
        line_total = item_data.quantity * item_data.unit_price * (1 - (item_data.discount_percent or 0) / 100)
        item_tax = line_total * (item_data.tax_rate or 0)
        
        line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            line_number=idx,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent or 0,
            line_total=line_total,
            tax_rate=item_data.tax_rate or 0,
            tax_amount=item_tax,
        )
        db.add(line_item)
    
    db.commit()
    db.refresh(invoice)
    
    # Load line items
    line_items = db.query(InvoiceLineItem).filter(
        InvoiceLineItem.invoice_id == invoice.id
    ).order_by(InvoiceLineItem.line_number).all()
    
    return InvoiceResponse(
        id=str(invoice.id),
        customer_id=str(invoice.customer_id),
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        payment_terms=invoice.payment_terms,
        notes=invoice.notes,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
        paid_amount=invoice.paid_amount,
        balance_amount=invoice.balance_amount,
        status=invoice.status,
        currency_code=invoice.currency_code,
        line_items=[
            InvoiceLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
            )
            for item in line_items
        ],
        created_at=invoice.created_at,
    )

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    if invoice.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update paid invoice",
        )
    
    # Update fields
    update_data = invoice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    
    # Load line items
    invoice.line_items = db.query(InvoiceLineItem).filter(
        InvoiceLineItem.invoice_id == invoice.id
    ).order_by(InvoiceLineItem.line_number).all()
    
    return InvoiceResponse(
        id=str(invoice.id),
        customer_id=str(invoice.customer_id),
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        payment_terms=invoice.payment_terms,
        notes=invoice.notes,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
        paid_amount=invoice.paid_amount,
        balance_amount=invoice.balance_amount,
        status=invoice.status,
        currency_code=invoice.currency_code,
        line_items=[
            InvoiceLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
            )
            for item in line_items
        ],
        created_at=invoice.created_at,
    )

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete invoice (soft delete)"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None),
        Invoice.status == "draft"
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found or cannot be deleted",
        )
    
    invoice.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Invoice deleted successfully"}

@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send invoice to customer"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    invoice.status = "sent"
    db.commit()
    
    # TODO: Send email to customer
    
    return {"success": True, "message": "Invoice sent successfully"}

@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    payment_date: Optional[date] = None,
    payment_method: Optional[str] = None,
    payment_reference: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark invoice as paid"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id,
        Invoice.deleted_at.is_(None)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    invoice.status = "paid"
    invoice.payment_date = payment_date or date.today()
    invoice.payment_method = payment_method
    invoice.payment_reference = payment_reference
    invoice.paid_amount = invoice.total_amount
    invoice.balance_amount = 0
    
    db.commit()
    
    return {"success": True, "message": "Invoice marked as paid"}

