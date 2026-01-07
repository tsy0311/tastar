"""
Integration Endpoints
Handles ERP, accounting software, and email service integrations
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.models import User, Customer, Invoice, Bill
from app.core.dependencies import get_current_active_user
from app.services.integration_service import integration_service

router = APIRouter()

class ERPConfig(BaseModel):
    erp_type: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class AccountingConfig(BaseModel):
    accounting_type: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class EmailConfig(BaseModel):
    email_type: str = "sendgrid"
    api_key: Optional[str] = None

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    from_email: Optional[str] = None

@router.post("/erp/configure")
async def configure_erp(
    config: ERPConfig,
    current_user: User = Depends(get_current_active_user)
):
    """Configure ERP integration"""
    try:
        integration_service.initialize_erp(
            config.erp_type,
            config.api_key,
            config.base_url
        )
        return {"success": True, "message": f"ERP integration configured: {config.erp_type}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/erp/sync/customers")
async def sync_customers_to_erp(
    customer_ids: Optional[List[str]] = Body(None, description="Specific customer IDs, or all if None"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync customers to ERP system"""
    if not integration_service.erp_service:
        raise HTTPException(status_code=400, detail="ERP integration not configured")
    
    try:
        # Get customers
        query = db.query(Customer).filter(Customer.company_id == current_user.company_id)
        if customer_ids:
            query = query.filter(Customer.id.in_(customer_ids))
        
        customers = query.all()
        
        # Format for ERP
        customer_data = [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "address": {
                    "line1": c.address_line1,
                    "line2": c.address_line2,
                    "city": c.city,
                    "state": c.state,
                    "postal_code": c.postal_code,
                    "country": c.country
                }
            }
            for c in customers
        ]
        
        result = await integration_service.erp_service.sync_customers(customer_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/erp/sync/invoices")
async def sync_invoices_to_erp(
    invoice_ids: Optional[List[str]] = Body(None, description="Specific invoice IDs, or all if None"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync invoices to ERP system"""
    if not integration_service.erp_service:
        raise HTTPException(status_code=400, detail="ERP integration not configured")
    
    try:
        # Get invoices
        query = db.query(Invoice).filter(Invoice.company_id == current_user.company_id)
        if invoice_ids:
            query = query.filter(Invoice.id.in_(invoice_ids))
        
        invoices = query.all()
        
        # Format for ERP
        invoice_data = [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "customer_id": str(inv.customer_id),
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "total_amount": float(inv.total_amount),
                "status": inv.status
            }
            for inv in invoices
        ]
        
        result = await integration_service.erp_service.sync_invoices(invoice_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/erp/inventory")
async def get_erp_inventory(
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory levels from ERP"""
    if not integration_service.erp_service:
        raise HTTPException(status_code=400, detail="ERP integration not configured")
    
    try:
        result = await integration_service.erp_service.get_inventory_levels()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounting/configure")
async def configure_accounting(
    config: AccountingConfig,
    current_user: User = Depends(get_current_active_user)
):
    """Configure accounting software integration"""
    try:
        integration_service.initialize_accounting(
            config.accounting_type,
            config.api_key,
            config.base_url
        )
        return {"success": True, "message": f"Accounting integration configured: {config.accounting_type}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounting/sync/transactions")
async def sync_transactions_to_accounting(
    transaction_ids: Optional[List[str]] = Body(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync transactions to accounting system"""
    if not integration_service.accounting_service:
        raise HTTPException(status_code=400, detail="Accounting integration not configured")
    
    try:
        # Get invoices and bills as transactions
        invoices = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status != "cancelled"
        ).all()
        
        bills = db.query(Bill).filter(
            Bill.company_id == current_user.company_id,
            Bill.status != "cancelled"
        ).all()
        
        transactions = []
        for inv in invoices:
            transactions.append({
                "type": "invoice",
                "id": str(inv.id),
                "date": inv.invoice_date.isoformat(),
                "amount": float(inv.total_amount),
                "description": f"Invoice {inv.invoice_number}"
            })
        
        for bill in bills:
            transactions.append({
                "type": "bill",
                "id": str(bill.id),
                "date": bill.bill_date.isoformat(),
                "amount": float(bill.total_amount),
                "description": f"Bill {bill.bill_number}"
            })
        
        result = await integration_service.accounting_service.sync_transactions(transactions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/configure")
async def configure_email(
    config: EmailConfig,
    current_user: User = Depends(get_current_active_user)
):
    """Configure email service integration"""
    try:
        integration_service.initialize_email(
            config.email_type,
            config.api_key
        )
        return {"success": True, "message": f"Email integration configured: {config.email_type}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/send")
async def send_email(
    email: EmailRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Send email via integration service"""
    if not integration_service.email_service:
        raise HTTPException(status_code=400, detail="Email integration not configured")
    
    try:
        result = await integration_service.email_service.send_email(
            email.to,
            email.subject,
            email.body,
            email.from_email
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email/send-bulk")
async def send_bulk_emails(
    emails: List[EmailRequest],
    current_user: User = Depends(get_current_active_user)
):
    """Send bulk emails"""
    if not integration_service.email_service:
        raise HTTPException(status_code=400, detail="Email integration not configured")
    
    try:
        email_data = [
            {
                "to": e.to,
                "subject": e.subject,
                "body": e.body,
                "from": e.from_email
            }
            for e in emails
        ]
        
        result = await integration_service.email_service.send_bulk_emails(email_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_integration_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of all integrations"""
    return {
        "success": True,
        "integrations": {
            "erp": {
                "configured": integration_service.erp_service is not None,
                "type": integration_service.erp_service.erp_type if integration_service.erp_service else None
            },
            "accounting": {
                "configured": integration_service.accounting_service is not None,
                "type": integration_service.accounting_service.accounting_type if integration_service.accounting_service else None
            },
            "email": {
                "configured": integration_service.email_service is not None,
                "type": integration_service.email_service.email_type if integration_service.email_service else None
            }
        }
    }


