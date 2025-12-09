"""
API Router - Main router that includes all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, companies, customers, invoices, payments

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

