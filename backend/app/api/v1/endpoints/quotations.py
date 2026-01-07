"""
Quotation Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, datetime
import uuid

from app.database.connection import get_db
from app.database.models import Quotation, QuotationLineItem, User, Customer, Invoice
from app.core.dependencies import get_current_active_user, require_role
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationLineItemCreate, QuotationLineItemResponse
)

router = APIRouter()

@router.get("", response_model=List[QuotationResponse])
async def list_quotations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    expired_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List quotations with filters"""
    query = db.query(Quotation).filter(
        Quotation.company_id == current_user.company_id
    )
    
    if search:
        query = query.filter(
            or_(
                Quotation.quotation_number.ilike(f"%{search}%"),
                Quotation.notes.ilike(f"%{search}%")
            )
        )
    
    if customer_id:
        try:
            query = query.filter(Quotation.customer_id == uuid.UUID(customer_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid customer ID format")
    
    if status_filter:
        query = query.filter(Quotation.status == status_filter)
    
    if date_from:
        query = query.filter(Quotation.quotation_date >= date_from)
    
    if date_to:
        query = query.filter(Quotation.quotation_date <= date_to)
    
    if expired_only:
        query = query.filter(
            Quotation.expiry_date.isnot(None),
            Quotation.expiry_date < date.today(),
            Quotation.status != "converted"
        )
    
    quotations = query.order_by(Quotation.quotation_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for quote in quotations:
        line_items = db.query(QuotationLineItem).filter(
            QuotationLineItem.quotation_id == quote.id
        ).order_by(QuotationLineItem.line_number).all()
        
        result.append(QuotationResponse(
            id=str(quote.id),
            company_id=str(quote.company_id),
            quotation_number=quote.quotation_number,
            customer_id=str(quote.customer_id),
            created_by=str(quote.created_by) if quote.created_by else None,
            approved_by=str(quote.approved_by) if quote.approved_by else None,
            quotation_date=quote.quotation_date,
            valid_until=quote.valid_until,
            expiry_date=quote.expiry_date,
            subtotal=quote.subtotal,
            tax_amount=quote.tax_amount,
            discount_amount=quote.discount_amount,
            shipping_amount=quote.shipping_amount,
            total_amount=quote.total_amount,
            currency_code=quote.currency_code,
            exchange_rate=quote.exchange_rate,
            status=quote.status,
            approval_status=quote.approval_status,
            notes=quote.notes,
            terms_conditions=quote.terms_conditions,
            line_items=[
                QuotationLineItemResponse(
                    id=str(item.id),
                    line_number=item.line_number,
                    description=item.description,
                    product_code=item.product_code,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_percent=item.discount_percent,
                    tax_rate=item.tax_rate,
                    material_id=str(item.material_id) if item.material_id else None,
                    job_id=str(item.job_id) if item.job_id else None,
                    discount_amount=item.discount_amount,
                    line_total=item.line_total,
                    tax_amount=item.tax_amount,
                    created_at=item.created_at,
                )
                for item in line_items
            ],
            created_at=quote.created_at,
            updated_at=quote.updated_at,
            approved_at=quote.approved_at,
        ))
    
    return result

@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quotation by ID"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    return QuotationResponse(
        id=str(quote.id),
        company_id=str(quote.company_id),
        quotation_number=quote.quotation_number,
        customer_id=str(quote.customer_id),
        created_by=str(quote.created_by) if quote.created_by else None,
        approved_by=str(quote.approved_by) if quote.approved_by else None,
        quotation_date=quote.quotation_date,
        valid_until=quote.valid_until,
        expiry_date=quote.expiry_date,
        subtotal=quote.subtotal,
        tax_amount=quote.tax_amount,
        discount_amount=quote.discount_amount,
        shipping_amount=quote.shipping_amount,
        total_amount=quote.total_amount,
        currency_code=quote.currency_code,
        exchange_rate=quote.exchange_rate,
        status=quote.status,
        approval_status=quote.approval_status,
        notes=quote.notes,
        terms_conditions=quote.terms_conditions,
        line_items=[
            QuotationLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                product_code=item.product_code,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                material_id=str(item.material_id) if item.material_id else None,
                job_id=str(item.job_id) if item.job_id else None,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                created_at=item.created_at,
            )
            for item in line_items
        ],
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        approved_at=quote.approved_at,
    )

@router.post("", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    quotation_data: QuotationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new quotation"""
    # Validate customer exists
    try:
        customer = db.query(Customer).filter(
            Customer.id == uuid.UUID(quotation_data.customer_id),
            Customer.company_id == current_user.company_id,
            Customer.deleted_at.is_(None)
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer ID format")
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if quotation number already exists
    existing = db.query(Quotation).filter(
        Quotation.company_id == current_user.company_id,
        Quotation.quotation_number == quotation_data.quotation_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Quotation number already exists")
    
    # Calculate totals
    subtotal = sum(
        item.quantity * item.unit_price * (1 - (item.discount_percent or 0) / 100)
        for item in quotation_data.line_items
    )
    tax_amount = sum(
        item.quantity * item.unit_price * (1 - (item.discount_percent or 0) / 100) * (item.tax_rate or 0)
        for item in quotation_data.line_items
    )
    discount_amount = sum(
        item.quantity * item.unit_price * (item.discount_percent or 0) / 100
        for item in quotation_data.line_items
    )
    shipping_amount = 0  # Can be added later
    total_amount = subtotal + tax_amount + shipping_amount
    
    # Create quotation
    quote = Quotation(
        company_id=current_user.company_id,
        customer_id=uuid.UUID(quotation_data.customer_id),
        created_by=current_user.id,
        quotation_number=quotation_data.quotation_number,
        quotation_date=quotation_data.quotation_date,
        valid_until=quotation_data.valid_until,
        expiry_date=quotation_data.expiry_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        currency_code=quotation_data.currency_code,
        exchange_rate=quotation_data.exchange_rate,
        notes=quotation_data.notes,
        terms_conditions=quotation_data.terms_conditions,
        status="draft"
    )
    
    db.add(quote)
    db.flush()
    
    # Create line items
    for line_item_data in quotation_data.line_items:
        line_total = line_item_data.quantity * line_item_data.unit_price * (1 - (line_item_data.discount_percent or 0) / 100)
        discount_amount_item = line_item_data.quantity * line_item_data.unit_price * (line_item_data.discount_percent or 0) / 100
        tax_amount_item = line_total * (line_item_data.tax_rate or 0)
        
        line_item = QuotationLineItem(
            quotation_id=quote.id,
            line_number=line_item_data.line_number,
            description=line_item_data.description,
            product_code=line_item_data.product_code,
            product_name=line_item_data.product_name,
            quantity=line_item_data.quantity,
            unit_price=line_item_data.unit_price,
            discount_percent=line_item_data.discount_percent or 0,
            discount_amount=discount_amount_item,
            line_total=line_total,
            tax_rate=line_item_data.tax_rate or 0,
            tax_amount=tax_amount_item,
            material_id=uuid.UUID(line_item_data.material_id) if line_item_data.material_id else None,
            job_id=uuid.UUID(line_item_data.job_id) if line_item_data.job_id else None,
        )
        db.add(line_item)
    
    db.commit()
    db.refresh(quote)
    
    # Load line items
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    return QuotationResponse(
        id=str(quote.id),
        company_id=str(quote.company_id),
        quotation_number=quote.quotation_number,
        customer_id=str(quote.customer_id),
        created_by=str(quote.created_by) if quote.created_by else None,
        approved_by=str(quote.approved_by) if quote.approved_by else None,
        quotation_date=quote.quotation_date,
        valid_until=quote.valid_until,
        expiry_date=quote.expiry_date,
        subtotal=quote.subtotal,
        tax_amount=quote.tax_amount,
        discount_amount=quote.discount_amount,
        shipping_amount=quote.shipping_amount,
        total_amount=quote.total_amount,
        currency_code=quote.currency_code,
        exchange_rate=quote.exchange_rate,
        status=quote.status,
        approval_status=quote.approval_status,
        notes=quote.notes,
        terms_conditions=quote.terms_conditions,
        line_items=[
            QuotationLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                product_code=item.product_code,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                material_id=str(item.material_id) if item.material_id else None,
                job_id=str(item.job_id) if item.job_id else None,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                created_at=item.created_at,
            )
            for item in line_items
        ],
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        approved_at=quote.approved_at,
    )

@router.put("/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: str,
    quotation_data: QuotationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update quotation"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quote.status in ['sent', 'accepted', 'converted']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update quotation with status: {quote.status}"
        )
    
    update_data = quotation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quote, field, value)
    
    db.commit()
    db.refresh(quote)
    
    # Load line items
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    return QuotationResponse(
        id=str(quote.id),
        company_id=str(quote.company_id),
        quotation_number=quote.quotation_number,
        customer_id=str(quote.customer_id),
        created_by=str(quote.created_by) if quote.created_by else None,
        approved_by=str(quote.approved_by) if quote.approved_by else None,
        quotation_date=quote.quotation_date,
        valid_until=quote.valid_until,
        expiry_date=quote.expiry_date,
        subtotal=quote.subtotal,
        tax_amount=quote.tax_amount,
        discount_amount=quote.discount_amount,
        shipping_amount=quote.shipping_amount,
        total_amount=quote.total_amount,
        currency_code=quote.currency_code,
        exchange_rate=quote.exchange_rate,
        status=quote.status,
        approval_status=quote.approval_status,
        notes=quote.notes,
        terms_conditions=quote.terms_conditions,
        line_items=[
            QuotationLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                product_code=item.product_code,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                material_id=str(item.material_id) if item.material_id else None,
                job_id=str(item.job_id) if item.job_id else None,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                created_at=item.created_at,
            )
            for item in line_items
        ],
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        approved_at=quote.approved_at,
    )

@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete quotation"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quote.status in ['accepted', 'converted']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete quotation with status: {quote.status}"
        )
    
    # Delete line items (cascade)
    db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).delete()
    
    db.delete(quote)
    db.commit()
    
    return None

@router.post("/{quotation_id}/send", response_model=QuotationResponse)
async def send_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send quotation to customer"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quote.status not in ["draft", "pending"]:
        raise HTTPException(status_code=400, detail=f"Cannot send quotation with status: {quote.status}")
    
    quote.status = "sent"
    db.commit()
    db.refresh(quote)
    
    # Load line items
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    return QuotationResponse(
        id=str(quote.id),
        company_id=str(quote.company_id),
        quotation_number=quote.quotation_number,
        customer_id=str(quote.customer_id),
        created_by=str(quote.created_by) if quote.created_by else None,
        approved_by=str(quote.approved_by) if quote.approved_by else None,
        quotation_date=quote.quotation_date,
        valid_until=quote.valid_until,
        expiry_date=quote.expiry_date,
        subtotal=quote.subtotal,
        tax_amount=quote.tax_amount,
        discount_amount=quote.discount_amount,
        shipping_amount=quote.shipping_amount,
        total_amount=quote.total_amount,
        currency_code=quote.currency_code,
        exchange_rate=quote.exchange_rate,
        status=quote.status,
        approval_status=quote.approval_status,
        notes=quote.notes,
        terms_conditions=quote.terms_conditions,
        line_items=[
            QuotationLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                product_code=item.product_code,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                material_id=str(item.material_id) if item.material_id else None,
                job_id=str(item.job_id) if item.job_id else None,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                created_at=item.created_at,
            )
            for item in line_items
        ],
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        approved_at=quote.approved_at,
    )

@router.post("/{quotation_id}/convert-to-invoice", response_model=dict)
async def convert_quotation_to_invoice(
    quotation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Convert quotation to invoice"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quote.status == "converted":
        raise HTTPException(status_code=400, detail="Quotation already converted")
    
    # Import invoice schemas
    from app.schemas.invoice import InvoiceCreate, InvoiceLineItemCreate
    from app.api.v1.endpoints.invoices import create_invoice
    
    # Get line items
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    # Create invoice from quotation
    invoice_data = InvoiceCreate(
        customer_id=str(quote.customer_id),
        invoice_date=date.today(),
        due_date=date.today(),  # Calculate based on payment terms
        payment_terms="Net 30",
        notes=f"Converted from quotation {quote.quotation_number}",
        line_items=[
            InvoiceLineItemCreate(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
            )
            for item in line_items
        ]
    )
    
    # Create invoice (reuse create_invoice logic)
    from app.database.models import Invoice, InvoiceLineItem, Customer
    
    customer = db.query(Customer).filter(
        Customer.id == quote.customer_id,
        Customer.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate invoice number
    max_invoice = db.query(Invoice).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_number.like('INV-%')
    ).order_by(Invoice.invoice_number.desc()).first()
    
    import re
    if max_invoice:
        match = re.search(r'(\d+)$', max_invoice.invoice_number)
        max_num = int(match.group(1)) if match else 0
    else:
        max_num = 0
    
    invoice_number = f"INV-{str(max_num + 1).zfill(6)}"
    
    # Calculate totals
    subtotal = quote.subtotal
    tax_amount = quote.tax_amount
    total_amount = quote.total_amount
    
    # Create invoice
    invoice = Invoice(
        company_id=current_user.company_id,
        customer_id=quote.customer_id,
        quotation_id=quote.id,
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
    for idx, quote_item in enumerate(line_items, 1):
        line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            line_number=idx,
            description=quote_item.description,
            product_code=quote_item.product_code,
            product_name=quote_item.product_name,
            quantity=quote_item.quantity,
            unit_price=quote_item.unit_price,
            discount_percent=quote_item.discount_percent,
            line_total=quote_item.line_total,
            tax_rate=quote_item.tax_rate,
            tax_amount=quote_item.tax_amount,
        )
        db.add(line_item)
    
    # Mark quotation as converted
    quote.status = "converted"
    
    db.commit()
    db.refresh(invoice)
    
    return {
        "success": True,
        "message": "Quotation converted to invoice successfully",
        "quotation_id": str(quote.id),
        "invoice_id": str(invoice.id),
        "invoice_number": invoice.invoice_number
    }

@router.post("/{quotation_id}/approve", response_model=QuotationResponse)
async def approve_quotation(
    quotation_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve quotation"""
    try:
        quote = db.query(Quotation).filter(
            Quotation.id == uuid.UUID(quotation_id),
            Quotation.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quotation ID format")
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if quote.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft quotations can be approved")
    
    quote.approval_status = "approved"
    quote.approved_by = current_user.id
    quote.approved_at = datetime.utcnow()
    quote.status = "pending"  # Ready to send
    
    db.commit()
    db.refresh(quote)
    
    # Load line items
    line_items = db.query(QuotationLineItem).filter(
        QuotationLineItem.quotation_id == quote.id
    ).order_by(QuotationLineItem.line_number).all()
    
    return QuotationResponse(
        id=str(quote.id),
        company_id=str(quote.company_id),
        quotation_number=quote.quotation_number,
        customer_id=str(quote.customer_id),
        created_by=str(quote.created_by) if quote.created_by else None,
        approved_by=str(quote.approved_by) if quote.approved_by else None,
        quotation_date=quote.quotation_date,
        valid_until=quote.valid_until,
        expiry_date=quote.expiry_date,
        subtotal=quote.subtotal,
        tax_amount=quote.tax_amount,
        discount_amount=quote.discount_amount,
        shipping_amount=quote.shipping_amount,
        total_amount=quote.total_amount,
        currency_code=quote.currency_code,
        exchange_rate=quote.exchange_rate,
        status=quote.status,
        approval_status=quote.approval_status,
        notes=quote.notes,
        terms_conditions=quote.terms_conditions,
        line_items=[
            QuotationLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                description=item.description,
                product_code=item.product_code,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_rate=item.tax_rate,
                material_id=str(item.material_id) if item.material_id else None,
                job_id=str(item.job_id) if item.job_id else None,
                discount_amount=item.discount_amount,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                created_at=item.created_at,
            )
            for item in line_items
        ],
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        approved_at=quote.approved_at,
    )

