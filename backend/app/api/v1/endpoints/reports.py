"""
Financial Reporting Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.database.connection import get_db
from app.database.models import Invoice, Payment, Bill, Customer, Supplier, User
from app.core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/aging-receivables")
async def get_aging_receivables(
    as_of_date: Optional[date] = Query(None, description="Report date (defaults to today)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get accounts receivable aging report"""
    report_date = as_of_date or date.today()
    
    # Get all unpaid invoices
    invoices = db.query(Invoice).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.status.in_(['sent', 'viewed', 'partial', 'overdue']),
        Invoice.balance_amount > 0,
        Invoice.deleted_at.is_(None)
    ).all()
    
    # Calculate aging buckets
    current = Decimal("0")
    days_30 = Decimal("0")
    days_60 = Decimal("0")
    days_90 = Decimal("0")
    days_90_plus = Decimal("0")
    
    aging_details = []
    
    for invoice in invoices:
        days_overdue = (report_date - invoice.due_date).days if invoice.due_date < report_date else 0
        
        if days_overdue <= 0:
            bucket = "current"
            current += invoice.balance_amount
        elif days_overdue <= 30:
            bucket = "1-30"
            days_30 += invoice.balance_amount
        elif days_overdue <= 60:
            bucket = "31-60"
            days_60 += invoice.balance_amount
        elif days_overdue <= 90:
            bucket = "61-90"
            days_90 += invoice.balance_amount
        else:
            bucket = "90+"
            days_90_plus += invoice.balance_amount
        
        # Get customer name
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        
        aging_details.append({
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "customer_id": str(invoice.customer_id),
            "customer_name": customer.name if customer else "Unknown",
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "days_overdue": days_overdue,
            "balance_amount": float(invoice.balance_amount),
            "total_amount": float(invoice.total_amount),
            "aging_bucket": bucket
        })
    
    total = current + days_30 + days_60 + days_90 + days_90_plus
    
    return {
        "success": True,
        "report_date": report_date.isoformat(),
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

@router.get("/aging-payables")
async def get_aging_payables(
    as_of_date: Optional[date] = Query(None, description="Report date (defaults to today)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get accounts payable aging report"""
    report_date = as_of_date or date.today()
    
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
        days_overdue = (report_date - bill.due_date).days if bill.due_date < report_date else 0
        
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
        
        # Get supplier name
        supplier = db.query(Supplier).filter(Supplier.id == bill.supplier_id).first()
        
        aging_details.append({
            "bill_id": str(bill.id),
            "bill_number": bill.bill_number,
            "vendor_invoice_number": bill.vendor_invoice_number,
            "supplier_id": str(bill.supplier_id),
            "supplier_name": supplier.name if supplier else "Unknown",
            "bill_date": bill.bill_date.isoformat(),
            "due_date": bill.due_date.isoformat(),
            "days_overdue": days_overdue,
            "balance_amount": float(bill.balance_amount),
            "total_amount": float(bill.total_amount),
            "aging_bucket": bucket
        })
    
    total = current + days_30 + days_60 + days_90 + days_90_plus
    
    return {
        "success": True,
        "report_date": report_date.isoformat(),
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

@router.get("/profit-loss")
async def get_profit_loss(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get Profit & Loss statement"""
    # Revenue (from invoices)
    revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    ).scalar() or Decimal("0")
    
    # Cost of Goods Sold (from bills - simplified)
    cogs = db.query(func.sum(Bill.total_amount)).filter(
        Bill.company_id == current_user.company_id,
        Bill.bill_date >= start_date,
        Bill.bill_date <= end_date,
        Bill.status != "cancelled"
    ).scalar() or Decimal("0")
    
    # Gross Profit
    gross_profit = revenue - cogs
    
    # Expenses (simplified - can be expanded)
    expenses = Decimal("0")  # Placeholder
    
    # Net Profit
    net_profit = gross_profit - expenses
    
    return {
        "success": True,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "revenue": {
            "total": float(revenue),
            "breakdown": {
                "invoices": float(revenue)
            }
        },
        "cost_of_goods_sold": {
            "total": float(cogs),
            "breakdown": {
                "bills": float(cogs)
            }
        },
        "gross_profit": float(gross_profit),
        "expenses": {
            "total": float(expenses),
            "breakdown": {}
        },
        "net_profit": float(net_profit)
    }

@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date = Query(..., description="Balance sheet date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get Balance Sheet"""
    # Assets
    # Accounts Receivable
    ar = db.query(func.sum(Invoice.balance_amount)).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.balance_amount > 0,
        Invoice.deleted_at.is_(None)
    ).scalar() or Decimal("0")
    
    # Liabilities
    # Accounts Payable
    ap = db.query(func.sum(Bill.balance_amount)).filter(
        Bill.company_id == current_user.company_id,
        Bill.balance_amount > 0
    ).scalar() or Decimal("0")
    
    # Equity (simplified)
    equity = Decimal("0")  # Placeholder
    
    return {
        "success": True,
        "as_of_date": as_of_date.isoformat(),
        "assets": {
            "current_assets": {
                "accounts_receivable": float(ar),
                "total": float(ar)
            },
            "total_assets": float(ar)
        },
        "liabilities": {
            "current_liabilities": {
                "accounts_payable": float(ap),
                "total": float(ap)
            },
            "total_liabilities": float(ap)
        },
        "equity": {
            "total": float(equity)
        },
        "total_liabilities_and_equity": float(ap + equity)
    }

