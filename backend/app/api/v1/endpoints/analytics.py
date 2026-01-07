"""
Advanced Analytics Endpoints
Provides business intelligence, trends, predictions, and insights
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import date, datetime, timedelta
from decimal import Decimal
import statistics

from app.database.connection import get_db
from app.database.models import (
    Invoice, Payment, Bill, Customer, Supplier, 
    PurchaseOrder, Quotation, Material, User
)
from app.core.dependencies import get_current_active_user
from app.core.cache import cached
from app.core.query_optimizer import optimize_list_query

router = APIRouter()

@router.get("/revenue-trends")
@cached(ttl=3600, key_prefix="analytics")
async def get_revenue_trends(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    granularity: str = Query("month", regex="^(day|week|month|quarter|year)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get revenue trends over time"""
    
    # Build query
    query = db.query(
        Invoice.invoice_date,
        func.sum(Invoice.total_amount).label('revenue')
    ).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    )
    
    # Group by granularity
    if granularity == "day":
        query = query.group_by(Invoice.invoice_date)
        query = query.order_by(Invoice.invoice_date)
    elif granularity == "week":
        query = query.group_by(
            extract('year', Invoice.invoice_date),
            extract('week', Invoice.invoice_date)
        )
    elif granularity == "month":
        query = query.group_by(
            extract('year', Invoice.invoice_date),
            extract('month', Invoice.invoice_date)
        )
    elif granularity == "quarter":
        query = query.group_by(
            extract('year', Invoice.invoice_date),
            extract('quarter', Invoice.invoice_date)
        )
    elif granularity == "year":
        query = query.group_by(extract('year', Invoice.invoice_date))
    
    results = query.all()
    
    trends = []
    for row in results:
        trends.append({
            "period": str(row.invoice_date) if granularity == "day" else f"{row.invoice_date}",
            "revenue": float(row.revenue or 0),
            "invoice_count": 1  # Simplified
        })
    
    # Calculate statistics
    revenues = [t['revenue'] for t in trends]
    stats = {
        "total_revenue": sum(revenues),
        "average_revenue": statistics.mean(revenues) if revenues else 0,
        "median_revenue": statistics.median(revenues) if revenues else 0,
        "max_revenue": max(revenues) if revenues else 0,
        "min_revenue": min(revenues) if revenues else 0,
        "growth_rate": ((revenues[-1] - revenues[0]) / revenues[0] * 100) if len(revenues) > 1 and revenues[0] > 0 else 0
    }
    
    return {
        "success": True,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": granularity
        },
        "trends": trends,
        "statistics": stats
    }

@router.get("/customer-analytics")
@cached(ttl=1800, key_prefix="analytics")
async def get_customer_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get customer analytics and insights"""
    
    # Top customers by revenue
    top_customers = db.query(
        Customer.id,
        Customer.name,
        func.sum(Invoice.total_amount).label('total_revenue'),
        func.count(Invoice.id).label('invoice_count')
    ).join(
        Invoice, Invoice.customer_id == Customer.id
    ).filter(
        Customer.company_id == current_user.company_id,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    ).group_by(
        Customer.id, Customer.name
    ).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(10).all()
    
    # Customer lifetime value
    customer_lifetime = db.query(
        Customer.id,
        Customer.name,
        func.sum(Invoice.total_amount).label('lifetime_value'),
        func.min(Invoice.invoice_date).label('first_purchase'),
        func.max(Invoice.invoice_date).label('last_purchase')
    ).join(
        Invoice, Invoice.customer_id == Customer.id
    ).filter(
        Customer.company_id == current_user.company_id,
        Invoice.status != "cancelled"
    ).group_by(
        Customer.id, Customer.name
    ).all()
    
    # Customer retention
    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.company_id == current_user.company_id
    ).scalar()
    
    active_customers = db.query(func.count(func.distinct(Invoice.customer_id))).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= date.today() - timedelta(days=90),
        Invoice.status != "cancelled"
    ).scalar()
    
    return {
        "success": True,
        "top_customers": [
            {
                "customer_id": str(c.id),
                "name": c.name,
                "total_revenue": float(c.total_revenue or 0),
                "invoice_count": c.invoice_count
            }
            for c in top_customers
        ],
        "customer_lifetime_value": [
            {
                "customer_id": str(c.id),
                "name": c.name,
                "lifetime_value": float(c.lifetime_value or 0),
                "first_purchase": c.first_purchase.isoformat() if c.first_purchase else None,
                "last_purchase": c.last_purchase.isoformat() if c.last_purchase else None
            }
            for c in customer_lifetime[:20]
        ],
        "retention_metrics": {
            "total_customers": total_customers,
            "active_customers_90d": active_customers,
            "retention_rate": (active_customers / total_customers * 100) if total_customers > 0 else 0
        }
    }

@router.get("/sales-forecast")
@cached(ttl=3600, key_prefix="analytics")
async def get_sales_forecast(
    forecast_days: int = Query(30, ge=7, le=365, description="Days to forecast"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sales forecast using historical data"""
    
    # Get historical data (last 90 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    daily_revenue = db.query(
        Invoice.invoice_date,
        func.sum(Invoice.total_amount).label('revenue')
    ).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    ).group_by(
        Invoice.invoice_date
    ).order_by(
        Invoice.invoice_date
    ).all()
    
    # Simple moving average forecast
    revenues = [float(r.revenue or 0) for r in daily_revenue]
    if revenues:
        avg_daily = statistics.mean(revenues)
        trend = (revenues[-1] - revenues[0]) / len(revenues) if len(revenues) > 1 else 0
    else:
        avg_daily = 0
        trend = 0
    
    # Generate forecast
    forecast = []
    for i in range(1, forecast_days + 1):
        forecast_date = end_date + timedelta(days=i)
        predicted_revenue = avg_daily + (trend * i)
        forecast.append({
            "date": forecast_date.isoformat(),
            "predicted_revenue": max(0, predicted_revenue),
            "confidence": "medium"  # Simplified
        })
    
    return {
        "success": True,
        "forecast_period": {
            "start_date": (end_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=forecast_days)).isoformat(),
            "days": forecast_days
        },
        "historical_data": {
            "period_days": 90,
            "average_daily_revenue": avg_daily,
            "trend": trend
        },
        "forecast": forecast,
        "total_forecasted_revenue": sum(f['predicted_revenue'] for f in forecast)
    }

@router.get("/inventory-analytics")
@cached(ttl=1800, key_prefix="analytics")
async def get_inventory_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get inventory analytics and insights"""
    
    # Low stock items
    low_stock = db.query(Material).filter(
        Material.company_id == current_user.company_id,
        Material.current_stock <= Material.reorder_level
    ).all()
    
    # Stock value
    total_stock_value = db.query(
        func.sum(Material.current_stock * Material.unit_price)
    ).filter(
        Material.company_id == current_user.company_id
    ).scalar() or Decimal("0")
    
    # Top materials by usage
    top_materials = db.query(
        Material.id,
        Material.name,
        Material.current_stock,
        Material.reorder_level,
        Material.unit_price
    ).filter(
        Material.company_id == current_user.company_id
    ).order_by(
        Material.current_stock.asc()
    ).limit(10).all()
    
    return {
        "success": True,
        "low_stock_items": [
            {
                "material_id": str(m.id),
                "name": m.name,
                "current_stock": float(m.current_stock or 0),
                "reorder_level": float(m.reorder_level or 0),
                "unit_price": float(m.unit_price or 0)
            }
            for m in low_stock
        ],
        "total_stock_value": float(total_stock_value),
        "top_materials": [
            {
                "material_id": str(m.id),
                "name": m.name,
                "current_stock": float(m.current_stock or 0),
                "reorder_level": float(m.reorder_level or 0),
                "unit_price": float(m.unit_price or 0)
            }
            for m in top_materials
        ]
    }

@router.get("/dashboard-summary")
@cached(ttl=300, key_prefix="analytics")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard summary"""
    
    today = date.today()
    this_month_start = date(today.year, today.month, 1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Revenue metrics
    this_month_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= this_month_start,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    ).scalar() or Decimal("0")
    
    last_month_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.invoice_date >= last_month_start,
        Invoice.invoice_date <= last_month_end,
        Invoice.status != "cancelled",
        Invoice.deleted_at.is_(None)
    ).scalar() or Decimal("0")
    
    # Outstanding receivables
    outstanding_ar = db.query(func.sum(Invoice.balance_amount)).filter(
        Invoice.company_id == current_user.company_id,
        Invoice.balance_amount > 0,
        Invoice.deleted_at.is_(None)
    ).scalar() or Decimal("0")
    
    # Outstanding payables
    outstanding_ap = db.query(func.sum(Bill.balance_amount)).filter(
        Bill.company_id == current_user.company_id,
        Bill.balance_amount > 0
    ).scalar() or Decimal("0")
    
    # Pending POs
    pending_pos = db.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.company_id == current_user.company_id,
        PurchaseOrder.status.in_(['draft', 'sent', 'acknowledged'])
    ).scalar()
    
    # Pending quotations
    pending_quotations = db.query(func.count(Quotation.id)).filter(
        Quotation.company_id == current_user.company_id,
        Quotation.status.in_(['draft', 'sent', 'viewed'])
    ).scalar()
    
    revenue_growth = ((float(this_month_revenue) - float(last_month_revenue)) / float(last_month_revenue) * 100) if last_month_revenue > 0 else 0
    
    return {
        "success": True,
        "revenue": {
            "this_month": float(this_month_revenue),
            "last_month": float(last_month_revenue),
            "growth_percent": revenue_growth
        },
        "outstanding": {
            "accounts_receivable": float(outstanding_ar),
            "accounts_payable": float(outstanding_ap),
            "net_position": float(outstanding_ar - outstanding_ap)
        },
        "pending": {
            "purchase_orders": pending_pos,
            "quotations": pending_quotations
        },
        "updated_at": datetime.now().isoformat()
    }

