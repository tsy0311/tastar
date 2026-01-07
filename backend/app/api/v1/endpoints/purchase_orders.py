"""
Purchase Order Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, datetime
import uuid
import re

from app.database.connection import get_db
from app.database.models import PurchaseOrder, PurchaseOrderLineItem, User, Supplier
from app.core.dependencies import get_current_active_user, require_role
from app.schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    POLineItemCreate, POLineItemResponse
)

router = APIRouter()

@router.get("", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    supplier_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List purchase orders with filters"""
    query = db.query(PurchaseOrder).filter(
        PurchaseOrder.company_id == current_user.company_id
    )
    
    if search:
        query = query.filter(
            or_(
                PurchaseOrder.po_number.ilike(f"%{search}%"),
                PurchaseOrder.notes.ilike(f"%{search}%")
            )
        )
    
    if supplier_id:
        try:
            query = query.filter(PurchaseOrder.supplier_id == uuid.UUID(supplier_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid supplier ID format")
    
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)
    
    if date_from:
        query = query.filter(PurchaseOrder.po_date >= date_from)
    
    if date_to:
        query = query.filter(PurchaseOrder.po_date <= date_to)
    
    pos = query.order_by(PurchaseOrder.po_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for po in pos:
        line_items = db.query(PurchaseOrderLineItem).filter(
            PurchaseOrderLineItem.purchase_order_id == po.id
        ).order_by(PurchaseOrderLineItem.line_number).all()
        
        result.append(PurchaseOrderResponse(
            id=str(po.id),
            company_id=str(po.company_id),
            po_number=po.po_number,
            po_type=po.po_type,
            supplier_id=str(po.supplier_id),
            requested_by=str(po.requested_by) if po.requested_by else None,
            approved_by=str(po.approved_by) if po.approved_by else None,
            po_date=po.po_date,
            required_date=po.required_date,
            expected_delivery_date=po.expected_delivery_date,
            subtotal=po.subtotal,
            tax_amount=po.tax_amount,
            discount_amount=po.discount_amount,
            shipping_amount=po.shipping_amount,
            total_amount=po.total_amount,
            currency_code=po.currency_code,
            exchange_rate=po.exchange_rate,
            status=po.status,
            approval_status=po.approval_status,
            payment_terms=po.payment_terms,
            delivery_terms=po.delivery_terms,
            shipping_method=po.shipping_method,
            shipping_terms=po.shipping_terms,
            notes=po.notes,
            internal_notes=po.internal_notes,
            line_items=[
                POLineItemResponse(
                    id=str(item.id),
                    line_number=item.line_number,
                    material_id=str(item.material_id) if item.material_id else None,
                    material_code=item.material_code,
                    material_description=item.material_description,
                    quantity_ordered=item.quantity_ordered,
                    quantity_received=item.quantity_received,
                    quantity_pending=item.quantity_pending,
                    unit_price=item.unit_price,
                    discount_percent=item.discount_percent,
                    line_total=item.line_total,
                    expected_delivery_date=item.expected_delivery_date,
                    received_date=item.received_date,
                    status=item.status,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in line_items
            ],
            created_at=po.created_at,
            updated_at=po.updated_at,
            approved_at=po.approved_at,
        ))
    
    return result

@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    po_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get purchase order by ID"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new purchase order"""
    # Validate supplier exists
    try:
        supplier = db.query(Supplier).filter(
            Supplier.id == uuid.UUID(po_data.supplier_id),
            Supplier.company_id == current_user.company_id,
            Supplier.deleted_at.is_(None)
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid supplier ID format")
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Check if PO number already exists
    existing = db.query(PurchaseOrder).filter(
        PurchaseOrder.company_id == current_user.company_id,
        PurchaseOrder.po_number == po_data.po_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="PO number already exists")
    
    # Calculate totals from line items
    from decimal import Decimal
    subtotal = sum(
        item.quantity_ordered * item.unit_price * (1 - (item.discount_percent or 0) / 100)
        for item in po_data.line_items
    )
    tax_amount = Decimal("0")  # Calculate if needed
    discount_amount = Decimal("0")  # Calculate if needed
    shipping_amount = Decimal("0")  # Can be added later
    total_amount = subtotal + tax_amount - discount_amount + shipping_amount
    
    # Create PO
    po = PurchaseOrder(
        company_id=current_user.company_id,
        supplier_id=uuid.UUID(po_data.supplier_id),
        requested_by=current_user.id,
        po_number=po_data.po_number,
        po_type=po_data.po_type,
        po_date=po_data.po_date,
        required_date=po_data.required_date,
        expected_delivery_date=po_data.expected_delivery_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        currency_code=po_data.currency_code,
        exchange_rate=po_data.exchange_rate,
        payment_terms=po_data.payment_terms,
        delivery_terms=po_data.delivery_terms,
        shipping_method=po_data.shipping_method,
        shipping_terms=po_data.shipping_terms,
        notes=po_data.notes,
        internal_notes=po_data.internal_notes,
        status="draft"
    )
    
    db.add(po)
    db.flush()
    
    # Create line items
    for line_item_data in po_data.line_items:
        line_total = line_item_data.quantity_ordered * line_item_data.unit_price * (1 - (line_item_data.discount_percent or 0) / 100)
        
        line_item = PurchaseOrderLineItem(
            purchase_order_id=po.id,
            line_number=line_item_data.line_number,
            material_id=uuid.UUID(line_item_data.material_id) if line_item_data.material_id else None,
            material_code=line_item_data.material_code,
            material_description=line_item_data.material_description,
            quantity_ordered=line_item_data.quantity_ordered,
            quantity_pending=line_item_data.quantity_ordered,
            unit_price=line_item_data.unit_price,
            discount_percent=line_item_data.discount_percent or 0,
            line_total=line_total,
            expected_delivery_date=line_item_data.expected_delivery_date,
            status="pending"
        )
        db.add(line_item)
    
    db.commit()
    db.refresh(po)
    
    # Load line items for response
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    po_id: str,
    po_data: PurchaseOrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update purchase order"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Don't allow updates if already sent/approved
    if po.status in ['sent', 'acknowledged', 'received', 'closed']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update purchase order with status: {po.status}"
        )
    
    update_data = po_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(po, field, value)
    
    db.commit()
    db.refresh(po)
    
    # Load line items
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    po_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete purchase order (soft delete)"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if po.status in ['sent', 'acknowledged', 'received', 'closed']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete purchase order with status: {po.status}"
        )
    
    # Soft delete by setting status to cancelled
    po.status = "cancelled"
    db.commit()
    
    return None

@router.post("/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    po_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve purchase order"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if po.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft POs can be approved")
    
    po.approval_status = "approved"
    po.approved_by = current_user.id
    po.approved_at = datetime.utcnow()
    po.status = "pending"  # Ready to send
    
    db.commit()
    db.refresh(po)
    
    # Load line items
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

@router.post("/{po_id}/send", response_model=PurchaseOrderResponse)
async def send_purchase_order(
    po_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send purchase order to supplier"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if po.status not in ["pending", "draft"]:
        raise HTTPException(status_code=400, detail=f"Cannot send PO with status: {po.status}")
    
    po.status = "sent"
    db.commit()
    db.refresh(po)
    
    # Load line items
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

@router.post("/{po_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    po_id: str,
    line_item_receipts: List[dict],  # [{"line_item_id": "uuid", "quantity_received": 10}]
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record receipt of purchase order items"""
    try:
        po = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == uuid.UUID(po_id),
            PurchaseOrder.company_id == current_user.company_id
        ).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid PO ID format")
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Update line items
    for receipt in line_item_receipts:
        line_item_id = receipt.get("line_item_id")
        quantity_received = receipt.get("quantity_received", 0)
        
        if not line_item_id:
            continue
        
        try:
            line_item = db.query(PurchaseOrderLineItem).filter(
                PurchaseOrderLineItem.id == uuid.UUID(line_item_id),
                PurchaseOrderLineItem.purchase_order_id == po.id
            ).first()
        except ValueError:
            continue
        
        if line_item:
            line_item.quantity_received += quantity_received
            line_item.quantity_pending = line_item.quantity_ordered - line_item.quantity_received
            
            if line_item.quantity_received >= line_item.quantity_ordered:
                line_item.status = "received"
                line_item.received_date = date.today()
            elif line_item.quantity_received > 0:
                line_item.status = "partial"
            else:
                line_item.status = "pending"
    
    # Update PO status
    all_received = all(
        item.quantity_received >= item.quantity_ordered
        for item in po.line_items
    )
    partial_received = any(
        item.quantity_received > 0 and item.quantity_received < item.quantity_ordered
        for item in po.line_items
    )
    
    if all_received:
        po.status = "received"
    elif partial_received:
        po.status = "partially_received"
    
    db.commit()
    db.refresh(po)
    
    # Load line items
    line_items = db.query(PurchaseOrderLineItem).filter(
        PurchaseOrderLineItem.purchase_order_id == po.id
    ).order_by(PurchaseOrderLineItem.line_number).all()
    
    return PurchaseOrderResponse(
        id=str(po.id),
        company_id=str(po.company_id),
        po_number=po.po_number,
        po_type=po.po_type,
        supplier_id=str(po.supplier_id),
        requested_by=str(po.requested_by) if po.requested_by else None,
        approved_by=str(po.approved_by) if po.approved_by else None,
        po_date=po.po_date,
        required_date=po.required_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        discount_amount=po.discount_amount,
        shipping_amount=po.shipping_amount,
        total_amount=po.total_amount,
        currency_code=po.currency_code,
        exchange_rate=po.exchange_rate,
        status=po.status,
        approval_status=po.approval_status,
        payment_terms=po.payment_terms,
        delivery_terms=po.delivery_terms,
        shipping_method=po.shipping_method,
        shipping_terms=po.shipping_terms,
        notes=po.notes,
        internal_notes=po.internal_notes,
        line_items=[
            POLineItemResponse(
                id=str(item.id),
                line_number=item.line_number,
                material_id=str(item.material_id) if item.material_id else None,
                material_code=item.material_code,
                material_description=item.material_description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                quantity_pending=item.quantity_pending,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                line_total=item.line_total,
                expected_delivery_date=item.expected_delivery_date,
                received_date=item.received_date,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in line_items
        ],
        created_at=po.created_at,
        updated_at=po.updated_at,
        approved_at=po.approved_at,
    )

