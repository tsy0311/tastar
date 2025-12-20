"""
API Router - Main router that includes all endpoint routers
"""
from fastapi import APIRouter
<<<<<<< HEAD
from app.api.v1.endpoints import (
    auth, users, companies, customers, invoices, payments, 
    documents, ai_assistant, demo, suppliers, materials,
    purchase_orders, quotations, bills, matching, reports
)
=======
from app.api.v1.endpoints import auth, users, companies, customers, invoices, payments, cms
>>>>>>> 7f3ef9c67d131cfb3c61541bc1daed68b9fbcf2f

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
<<<<<<< HEAD
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo"])

# Purchasing Module
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])

# Sales Module
api_router.include_router(quotations.router, prefix="/quotations", tags=["Quotations"])

# Accounts Payable
api_router.include_router(bills.router, prefix="/bills", tags=["Bills"])

# Transaction Matching
api_router.include_router(matching.router, prefix="/matching", tags=["Transaction Matching"])

# Financial Reporting
api_router.include_router(reports.router, prefix="/reports", tags=["Financial Reports"])
=======
api_router.include_router(cms.router, prefix="/cms", tags=["CMS & AI Suggestions"])
>>>>>>> 7f3ef9c67d131cfb3c61541bc1daed68b9fbcf2f

