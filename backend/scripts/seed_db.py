"""
Database Seeding Script
"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, init_db
from app.database.models import Company, User, Role, Customer, UserRole
from app.core.security import get_password_hash
from app.core.logging import setup_logging

setup_logging()
from app.core.logging import logger

async def seed_database():
    """Seed database with initial data"""
    await init_db()
    db: Session = SessionLocal()
    
    try:
        logger.info("Seeding database...")
        
        # Create default company
        company = db.query(Company).filter(Company.name == "Demo Company").first()
        if not company:
            company = Company(
                name="Demo Company",
                country="US",
                currency_code="USD",
                subscription_status="active"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            logger.info("Created demo company")
        else:
            logger.info("Using existing demo company")
        
        # Create default roles
        admin_role = db.query(Role).filter(
            Role.company_id == company.id,
            Role.name == "admin"
        ).first()
        
        if not admin_role:
            admin_role = Role(
                company_id=company.id,
                name="admin",
                description="Administrator with full access",
                is_system_role=True
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        accountant_role = db.query(Role).filter(
            Role.company_id == company.id,
            Role.name == "accountant"
        ).first()
        
        if not accountant_role:
            accountant_role = Role(
                company_id=company.id,
                name="accountant",
                description="Accounting module access",
                is_system_role=True
            )
            db.add(accountant_role)
            db.commit()
            db.refresh(accountant_role)
        
        logger.info("Created default roles")
        
        # Create default admin user
        user = db.query(User).filter(User.email == "admin@demo.com").first()
        if not user:
            user = User(
                company_id=company.id,
                email="admin@demo.com",
                password_hash=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                status="active",
                email_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Assign admin role
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            db.add(user_role)
            db.commit()
            
            logger.info("Created default admin user: admin@demo.com / admin123")
        else:
            logger.info("Admin user already exists")
        
        # Create sample customer
        customer = db.query(Customer).filter(
            Customer.company_id == company.id,
            Customer.customer_code == "CUST-001"
        ).first()
        
        if not customer:
            customer = Customer(
                company_id=company.id,
                customer_code="CUST-001",
                name="Demo Customer",
                primary_email="customer@demo.com",
                status="active"
            )
            db.add(customer)
            db.commit()
            logger.info("Created sample customer")
        else:
            logger.info("Sample customer already exists")
        
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())

