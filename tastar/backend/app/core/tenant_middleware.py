"""
Multi-Tenant Support Middleware
Provides tenant isolation and multi-company management
"""
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.database.models import Company, User
from app.core.logging import logger

async def get_tenant_from_request(request: Request) -> Optional[str]:
    """
    Extract tenant/company ID from request
    Supports multiple methods:
    1. X-Tenant-ID header
    2. Subdomain
    3. Query parameter
    4. User's company_id (from JWT)
    """
    # Method 1: Header
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    
    # Method 2: Subdomain (if using subdomain-based multi-tenancy)
    host = request.headers.get("host", "")
    if host:
        subdomain = host.split(".")[0]
        # Validate subdomain is not common domains
        if subdomain not in ["www", "api", "app", "admin"]:
            # Could map subdomain to tenant_id
            pass
    
    # Method 3: Query parameter
    tenant_id = request.query_params.get("tenant_id")
    if tenant_id:
        return tenant_id
    
    return None

async def validate_tenant_access(
    tenant_id: str,
    user: User,
    db: Session
) -> bool:
    """
    Validate that user has access to the specified tenant/company
    """
    if not tenant_id:
        return False
    
    # Check if user belongs to the company
    if str(user.company_id) == tenant_id:
        return True
    
    # Check if user has access to multiple companies (for admin users)
    # This would require a user_companies association table
    # For now, just check direct company_id match
    
    return False

def enforce_tenant_isolation(query, model, user: User):
    """
    Automatically filter queries by company_id for tenant isolation
    """
    if hasattr(model, 'company_id'):
        return query.filter(model.company_id == user.company_id)
    return query

class TenantContext:
    """Context manager for tenant operations"""
    
    def __init__(self, tenant_id: str, user: User, db: Session):
        self.tenant_id = tenant_id
        self.user = user
        self.db = db
        self.original_company_id = user.company_id
    
    async def __aenter__(self):
        """Enter tenant context"""
        # Validate access
        if not await validate_tenant_access(self.tenant_id, self.user, self.db):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this tenant"
            )
        
        # Temporarily set user's company_id (if needed)
        # In production, you might want to use a different approach
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit tenant context"""
        # Restore original company_id if needed
        pass

def get_tenant_company(db: Session, tenant_id: str) -> Optional[Company]:
    """Get company by tenant ID"""
    try:
        return db.query(Company).filter(Company.id == tenant_id).first()
    except Exception as e:
        logger.error(f"Error getting tenant company: {e}")
        return None

async def switch_tenant_context(
    request: Request,
    user: User,
    db: Session
) -> Optional[str]:
    """
    Switch tenant context based on request
    Returns the tenant_id to use for queries
    """
    tenant_id = await get_tenant_from_request(request)
    
    if tenant_id:
        # Validate access
        if not await validate_tenant_access(tenant_id, user, db):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this tenant"
            )
        return tenant_id
    
    # Default to user's company_id
    return str(user.company_id)


