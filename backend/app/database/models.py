"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, Boolean, Text, ForeignKey, CheckConstraint, UniqueConstraint, Index, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

# Association table for many-to-many relationship
user_roles_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, server_default=func.now()),
    Column('assigned_by', UUID(as_uuid=True), ForeignKey('users.id')),
    Index('idx_user_roles_user_id', 'user_id'),
    Index('idx_user_roles_role_id', 'role_id'),
)

class Company(Base):
    """Company model"""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    tax_id = Column(String(50), unique=True)
    registration_number = Column(String(100))
    logo_url = Column(Text)
    website = Column(String(255))
    industry = Column(String(100))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(2), nullable=False, default="US")
    
    # Contact
    phone = Column(String(50))
    email = Column(String(255))
    
    # Settings
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en-US")
    currency_code = Column(String(3), default="USD")
    fiscal_year_start = Column(Date)
    
    # Subscription
    subscription_plan = Column(String(50))
    subscription_status = Column(String(20))
    subscription_expires_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    users = relationship("User", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    suppliers = relationship("Supplier")
    materials = relationship("Material")
    purchase_orders = relationship("PurchaseOrder")
    quotations = relationship("Quotation")
    documents = relationship("Document")
    bills = relationship("Bill")
    
    __table_args__ = (
        CheckConstraint(
            "subscription_status IN ('active', 'trial', 'expired', 'cancelled') OR subscription_status IS NULL",
            name="ck_companies_subscription_status"
        ),
        Index("idx_companies_name", "name"),
        Index("idx_companies_deleted_at", "deleted_at"),
    )

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identity
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    avatar_url = Column(Text)
    
    # Authentication
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    
    # Status
    status = Column(String(20), default="active")
    last_login_at = Column(DateTime)
    last_login_ip = Column(INET)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Preferences
    timezone = Column(String(50))
    locale = Column(String(10))
    notification_preferences = Column(JSONB)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    roles = relationship("Role", secondary=user_roles_table, back_populates="users")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'pending')",
            name="ck_users_status"
        ),
        Index("idx_users_company_id", "company_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_status", "status"),
        Index("idx_users_deleted_at", "deleted_at"),
    )

class Role(Base):
    """Role model"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles_table, back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uk_roles_company_name"),
        Index("idx_roles_company_id", "company_id"),
    )


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identity
    customer_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    tax_id = Column(String(50))
    
    # Classification
    customer_type = Column(String(50))
    industry = Column(String(100))
    segment = Column(String(50))
    
    # Address (billing)
    billing_address_line1 = Column(String(255))
    billing_address_line2 = Column(String(255))
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_postal_code = Column(String(20))
    billing_country = Column(String(2))
    
    # Address (shipping)
    shipping_address_line1 = Column(String(255))
    shipping_address_line2 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(2))
    
    # Contact
    primary_contact_name = Column(String(200))
    primary_email = Column(String(255))
    primary_phone = Column(String(50))
    website = Column(String(255))
    
    # Financial
    credit_limit = Column(Numeric(15, 2))
    payment_terms = Column(String(50))
    currency_code = Column(String(3), default="USD")
    tax_exempt = Column(Boolean, default=False)
    tax_rate = Column(Numeric(5, 4))
    
    # Status
    status = Column(String(20), default="active")
    
    # Analytics
    lifetime_value = Column(Numeric(15, 2), default=0)
    last_order_date = Column(Date)
    total_orders = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")
    
    __table_args__ = (
        UniqueConstraint("company_id", "customer_code", name="uk_customers_company_code"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'prospect', 'lead')",
            name="ck_customers_status"
        ),
        Index("idx_customers_company_id", "company_id"),
        Index("idx_customers_code", "customer_code"),
        Index("idx_customers_name", "name"),
        Index("idx_customers_status", "status"),
        Index("idx_customers_deleted_at", "deleted_at"),
    )

class Invoice(Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    invoice_number = Column(String(100), nullable=False)
    invoice_type = Column(String(20), default="standard")
    
    # Relationships
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True))
    quotation_id = Column(UUID(as_uuid=True))
    
    # Dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    currency_code = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(10, 6), default=1)
    
    # Status
    status = Column(String(20), default="draft")
    
    # Payment
    payment_terms = Column(String(50))
    payment_method = Column(String(50))
    payment_reference = Column(String(255))
    
    # Additional
    notes = Column(Text)
    internal_notes = Column(Text)
    reference_number = Column(String(255))
    
    # Approval
    approval_status = Column(String(20))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("company_id", "invoice_number", name="uk_invoices_company_number"),
        CheckConstraint(
            "invoice_type IN ('standard', 'proforma', 'credit', 'debit')",
            name="ck_invoices_type"
        ),
        CheckConstraint(
            "status IN ('draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'cancelled')",
            name="ck_invoices_status"
        ),
        Index("idx_invoices_company_id", "company_id"),
        Index("idx_invoices_customer_id", "customer_id"),
        Index("idx_invoices_number", "invoice_number"),
        Index("idx_invoices_date", "invoice_date"),
        Index("idx_invoices_due_date", "due_date"),
        Index("idx_invoices_status", "status"),
    )

class InvoiceLineItem(Base):
    """Invoice Line Item model"""
    __tablename__ = "invoice_line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    
    # Product/Service
    product_code = Column(String(100))
    product_name = Column(String(255))
    
    # Quantity & Pricing
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tax_rate = Column(Numeric(5, 4), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Reference
    job_id = Column(UUID(as_uuid=True))
    material_id = Column(UUID(as_uuid=True))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    
    __table_args__ = (
        UniqueConstraint("invoice_id", "line_number", name="uk_invoice_line_items_invoice_line"),
        Index("idx_invoice_line_items_invoice_id", "invoice_id"),
        Index("idx_invoice_line_items_job_id", "job_id"),
    )

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    payment_number = Column(String(100), nullable=False)
    payment_type = Column(String(20), nullable=False)
    
    # Relationships
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    supplier_id = Column(UUID(as_uuid=True))
    
    # Financial
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(10, 6), default=1)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_reference = Column(String(255))
    bank_account_id = Column(UUID(as_uuid=True))
    
    # Status
    status = Column(String(20), default="pending")
    
    # Additional
    notes = Column(Text)
    receipt_url = Column(Text)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    allocations = relationship("PaymentAllocation", back_populates="payment", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("company_id", "payment_number", name="uk_payments_company_number"),
        CheckConstraint(
            "payment_type IN ('receipt', 'payment')",
            name="ck_payments_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')",
            name="ck_payments_status"
        ),
        Index("idx_payments_company_id", "company_id"),
        Index("idx_payments_customer_id", "customer_id"),
        Index("idx_payments_supplier_id", "supplier_id"),
        Index("idx_payments_date", "payment_date"),
        Index("idx_payments_status", "status"),
    )

class PaymentAllocation(Base):
    """Payment Allocation model"""
    __tablename__ = "payment_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    bill_id = Column(UUID(as_uuid=True))
    
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    allocation_date = Column(Date, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    payment = relationship("Payment", back_populates="allocations")
    
    __table_args__ = (
        CheckConstraint(
            "(invoice_id IS NOT NULL AND bill_id IS NULL) OR (invoice_id IS NULL AND bill_id IS NOT NULL)",
            name="ck_payment_allocations_reference"
        ),
        Index("idx_payment_allocations_payment_id", "payment_id"),
        Index("idx_payment_allocations_invoice_id", "invoice_id"),
    )

# ============================================================================
# Purchasing Module Models
# ============================================================================

class Supplier(Base):
    """Supplier model"""
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identity
    supplier_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    tax_id = Column(String(50))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(2))
    
    # Contact
    primary_contact_name = Column(String(200))
    primary_email = Column(String(255))
    primary_phone = Column(String(50))
    website = Column(String(255))
    
    # Financial
    payment_terms = Column(String(50))
    currency_code = Column(String(3), default="USD")
    credit_limit = Column(Numeric(15, 2))
    
    # Performance
    on_time_delivery_rate = Column(Numeric(5, 2))
    quality_score = Column(Numeric(5, 2))
    average_rating = Column(Numeric(3, 2))
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(String(20), default="active")
    
    # Risk
    risk_score = Column(Integer)
    risk_level = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    __table_args__ = (
        UniqueConstraint("company_id", "supplier_code", name="uk_suppliers_company_code"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'pending', 'blacklisted')",
            name="ck_suppliers_status"
        ),
        Index("idx_suppliers_company_id", "company_id"),
        Index("idx_suppliers_code", "supplier_code"),
        Index("idx_suppliers_status", "status"),
    )

class Material(Base):
    """Material model"""
    __tablename__ = "materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    material_code = Column(String(100), nullable=False)
    material_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Classification
    category = Column(String(100))
    subcategory = Column(String(100))
    material_type = Column(String(50))
    
    # Specifications
    unit_of_measure = Column(String(20), nullable=False)
    weight = Column(Numeric(10, 3))
    dimensions = Column(String(100))
    specifications = Column(JSONB)
    
    # Inventory
    current_stock = Column(Numeric(10, 3), default=0)
    reorder_point = Column(Numeric(10, 3), default=0)
    reorder_quantity = Column(Numeric(10, 3))
    safety_stock = Column(Numeric(10, 3), default=0)
    max_stock = Column(Numeric(10, 3))
    
    # Pricing
    standard_cost = Column(Numeric(15, 4))
    average_cost = Column(Numeric(15, 4))
    last_purchase_price = Column(Numeric(15, 4))
    
    # Supplier
    preferred_supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    
    # Status
    status = Column(String(20), default="active")
    is_active = Column(Boolean, default=True)
    
    # Analytics
    abc_category = Column(String(1))
    turnover_rate = Column(Numeric(10, 2))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)
    
    # Relationships
    preferred_supplier = relationship("Supplier")
    
    __table_args__ = (
        UniqueConstraint("company_id", "material_code", name="uk_materials_company_code"),
        CheckConstraint(
            "material_type IN ('raw', 'component', 'finished_good', 'consumable', 'tooling')",
            name="ck_materials_type"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'obsolete')",
            name="ck_materials_status"
        ),
        Index("idx_materials_company_id", "company_id"),
        Index("idx_materials_code", "material_code"),
        Index("idx_materials_category", "category"),
        Index("idx_materials_status", "status"),
        Index("idx_materials_current_stock", "current_stock"),
    )

class PurchaseOrder(Base):
    """Purchase Order model"""
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    po_number = Column(String(100), nullable=False)
    po_type = Column(String(20), default="standard")
    
    # Relationships
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Dates
    po_date = Column(Date, nullable=False)
    required_date = Column(Date)
    expected_delivery_date = Column(Date)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    currency_code = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(10, 6), default=1)
    
    # Status
    status = Column(String(20), default="draft")
    approval_status = Column(String(20))
    
    # Shipping
    shipping_address_id = Column(UUID(as_uuid=True))
    shipping_method = Column(String(50))
    shipping_terms = Column(String(50))
    
    # Terms
    payment_terms = Column(String(50))
    delivery_terms = Column(String(50))
    
    # Additional
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    line_items = relationship("PurchaseOrderLineItem", back_populates="purchase_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("company_id", "po_number", name="uk_purchase_orders_company_number"),
        CheckConstraint(
            "po_type IN ('standard', 'blanket', 'contract')",
            name="ck_purchase_orders_type"
        ),
        CheckConstraint(
            "status IN ('draft', 'pending', 'sent', 'acknowledged', 'partially_received', 'received', 'closed', 'cancelled')",
            name="ck_purchase_orders_status"
        ),
        Index("idx_purchase_orders_company_id", "company_id"),
        Index("idx_purchase_orders_supplier_id", "supplier_id"),
        Index("idx_purchase_orders_number", "po_number"),
        Index("idx_purchase_orders_status", "status"),
        Index("idx_purchase_orders_date", "po_date"),
    )

class PurchaseOrderLineItem(Base):
    """Purchase Order Line Item model"""
    __tablename__ = "purchase_order_line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    
    # Material
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.id"))
    material_code = Column(String(100))
    material_description = Column(Text, nullable=False)
    
    # Quantity & Pricing
    quantity_ordered = Column(Numeric(10, 3), nullable=False)
    quantity_received = Column(Numeric(10, 3), default=0)
    quantity_pending = Column(Numeric(10, 3), nullable=False)
    
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Delivery
    expected_delivery_date = Column(Date)
    received_date = Column(Date)
    
    # Status
    status = Column(String(20), default="pending")
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    material = relationship("Material")
    
    __table_args__ = (
        UniqueConstraint("purchase_order_id", "line_number", name="uk_po_line_items_po_line"),
        CheckConstraint(
            "status IN ('pending', 'partial', 'received', 'cancelled')",
            name="ck_po_line_items_status"
        ),
        Index("idx_po_line_items_po_id", "purchase_order_id"),
    )

# ============================================================================
# Sales Module Models
# ============================================================================

class Quotation(Base):
    """Quotation model"""
    __tablename__ = "quotations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    quotation_number = Column(String(100), nullable=False)
    
    # Relationships
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Dates
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date)
    expiry_date = Column(Date)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    currency_code = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(10, 6), default=1)
    
    # Status
    status = Column(String(20), default="draft")
    approval_status = Column(String(20))
    
    # Additional
    notes = Column(Text)
    terms_conditions = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer")
    line_items = relationship("QuotationLineItem", back_populates="quotation", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("company_id", "quotation_number", name="uk_quotations_company_number"),
        CheckConstraint(
            "status IN ('draft', 'sent', 'viewed', 'accepted', 'rejected', 'expired', 'converted')",
            name="ck_quotations_status"
        ),
        Index("idx_quotations_company_id", "company_id"),
        Index("idx_quotations_customer_id", "customer_id"),
        Index("idx_quotations_number", "quotation_number"),
        Index("idx_quotations_status", "status"),
    )

class QuotationLineItem(Base):
    """Quotation Line Item model"""
    __tablename__ = "quotation_line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    
    # Product/Service
    product_code = Column(String(100))
    product_name = Column(String(255))
    
    # Quantity & Pricing
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tax_rate = Column(Numeric(5, 4), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Reference
    material_id = Column(UUID(as_uuid=True))
    job_id = Column(UUID(as_uuid=True))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    quotation = relationship("Quotation", back_populates="line_items")
    
    __table_args__ = (
        UniqueConstraint("quotation_id", "line_number", name="uk_quotation_line_items_quotation_line"),
        Index("idx_quotation_line_items_quotation_id", "quotation_id"),
    )

# ============================================================================
# Document Management Models
# ============================================================================

class Document(Base):
    """Document model for OCR and document management"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    document_type = Column(String(50), nullable=False)
    document_category = Column(String(50))
    
    # Reference
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))
    
    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    file_hash = Column(String(64))
    
    # OCR Processing
    ocr_status = Column(String(20), default="pending")
    ocr_processed_at = Column(DateTime)
    ocr_confidence_score = Column(Numeric(5, 2))
    extracted_data = Column(JSONB)
    
    # Validation
    validation_status = Column(String(20))
    validation_errors = Column(JSONB)
    
    # Metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('invoice', 'receipt', 'purchase_order', 'delivery_order', 'quotation', 'contract', 'other')",
            name="ck_documents_type"
        ),
        CheckConstraint(
            "ocr_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_documents_ocr_status"
        ),
        Index("idx_documents_company_id", "company_id"),
        Index("idx_documents_type", "document_type"),
        Index("idx_documents_reference", "reference_type", "reference_id"),
        Index("idx_documents_ocr_status", "ocr_status"),
    )

# ============================================================================
# Accounts Payable Models
# ============================================================================

class Bill(Base):
    """Bill model (Vendor Bills - Accounts Payable)"""
    __tablename__ = "bills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Identification
    bill_number = Column(String(100), nullable=False)
    vendor_invoice_number = Column(String(255))
    
    # Relationships
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"))
    
    # Dates
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    currency_code = Column(String(3), default="USD")
    
    # Status
    status = Column(String(20), default="draft")
    approval_status = Column(String(20))
    
    # Additional
    notes = Column(Text)
    attachment_url = Column(Text)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier")
    purchase_order = relationship("PurchaseOrder")
    
    __table_args__ = (
        UniqueConstraint("company_id", "bill_number", name="uk_bills_company_number"),
        CheckConstraint(
            "status IN ('draft', 'pending', 'approved', 'partial', 'paid', 'overdue', 'cancelled')",
            name="ck_bills_status"
        ),
        Index("idx_bills_company_id", "company_id"),
        Index("idx_bills_supplier_id", "supplier_id"),
        Index("idx_bills_due_date", "due_date"),
        Index("idx_bills_status", "status"),
    )

# ============================================================================
# Transaction Matching Models
# ============================================================================

class TransactionMatching(Base):
    """Transaction Matching model for three-way matching"""
    __tablename__ = "transaction_matching"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # References
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"))
    delivery_order_id = Column(UUID(as_uuid=True))
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"))
    
    # Matching Status
    match_type = Column(String(20))
    match_status = Column(String(20), default="pending")
    match_confidence_score = Column(Numeric(5, 2))
    
    # Variances
    amount_variance = Column(Numeric(15, 2))
    quantity_variance = Column(Numeric(10, 3))
    date_variance = Column(Integer)
    
    # Tolerance
    tolerance_threshold = Column(Numeric(5, 2))
    within_tolerance = Column(Boolean)
    
    # Exceptions
    exception_reason = Column(Text)
    exception_resolved = Column(Boolean, default=False)
    
    # Metadata
    matched_at = Column(DateTime)
    matched_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint(
            "match_type IN ('two_way', 'three_way')",
            name="ck_transaction_matching_type"
        ),
        CheckConstraint(
            "match_status IN ('pending', 'matched', 'partial', 'exception', 'resolved')",
            name="ck_transaction_matching_status"
        ),
        Index("idx_transaction_matching_company_id", "company_id"),
        Index("idx_transaction_matching_po_id", "purchase_order_id"),
        Index("idx_transaction_matching_status", "match_status"),
    )

