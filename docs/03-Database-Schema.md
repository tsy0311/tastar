# Database Schema Documentation
## Unified AI Business Assistant for CNC Factory

**Version:** 1.0  
**Database System:** PostgreSQL 15+  
**Last Updated:** 2024

---

## Overview

This document defines the complete database schema for the Unified AI Business Assistant application. The schema is designed to support all four core modules: Accounting, Purchasing, Sales, and Email/Chatbot.

### Database Design Principles

1. **Normalization:** 3NF (Third Normal Form) with strategic denormalization for performance
2. **Scalability:** Designed to handle millions of records
3. **Data Integrity:** Foreign keys, constraints, and triggers
4. **Audit Trail:** Comprehensive change tracking
5. **Multi-tenancy:** Support for multiple companies/organizations
6. **Performance:** Indexes optimized for common queries
7. **Flexibility:** Extensible schema for future enhancements

---

## Schema Diagram Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Core Entities                             │
├─────────────────────────────────────────────────────────────┤
│  Companies, Users, Roles, Permissions                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Accounting Module Tables                        │
├─────────────────────────────────────────────────────────────┤
│  Invoices, Payments, Transactions, Matching, Documents      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             Purchasing Module Tables                         │
├─────────────────────────────────────────────────────────────┤
│  Materials, Inventory, POs, Suppliers, Deliveries           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Sales Module Tables                             │
├─────────────────────────────────────────────────────────────┤
│  Customers, Quotations, Orders, Opportunities               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          Email/Chatbot Module Tables                         │
├─────────────────────────────────────────────────────────────┤
│  Emails, Conversations, Messages, Knowledge Base            │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Tables

### 1. Companies

Stores organization/company information (multi-tenancy support).

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(50),
    registration_number VARCHAR(100),
    logo_url TEXT,
    website VARCHAR(255),
    industry VARCHAR(100),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) NOT NULL,
    
    -- Contact
    phone VARCHAR(50),
    email VARCHAR(255),
    
    -- Settings
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    currency_code VARCHAR(3) DEFAULT 'USD',
    fiscal_year_start DATE,
    
    -- Subscription
    subscription_plan VARCHAR(50),
    subscription_status VARCHAR(20),
    subscription_expires_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_companies_tax_id UNIQUE (tax_id),
    CONSTRAINT ck_companies_subscription_status CHECK (subscription_status IN ('active', 'trial', 'expired', 'cancelled'))
);

CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_subscription_status ON companies(subscription_status);
CREATE INDEX idx_companies_deleted_at ON companies(deleted_at);
```

### 2. Users

User accounts with authentication information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identity
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    avatar_url TEXT,
    
    -- Authentication
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    last_login_at TIMESTAMP,
    last_login_ip INET,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- Preferences
    timezone VARCHAR(50),
    locale VARCHAR(10),
    notification_preferences JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_users_email UNIQUE (email),
    CONSTRAINT ck_users_status CHECK (status IN ('active', 'inactive', 'suspended', 'pending'))
);

CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);
```

### 3. Roles

Role definitions for RBAC (Role-Based Access Control).

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_roles_company_name UNIQUE (company_id, name)
);

CREATE INDEX idx_roles_company_id ON roles(company_id);
```

### 4. Permissions

Permission definitions.

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_permissions_resource_action UNIQUE (resource, action)
);

-- Common permissions
INSERT INTO permissions (resource, action, description) VALUES
('invoice', 'create', 'Create invoices'),
('invoice', 'read', 'View invoices'),
('invoice', 'update', 'Edit invoices'),
('invoice', 'delete', 'Delete invoices'),
('invoice', 'approve', 'Approve invoices'),
('purchase_order', 'create', 'Create purchase orders'),
('purchase_order', 'read', 'View purchase orders'),
('purchase_order', 'update', 'Edit purchase orders'),
('quotation', 'create', 'Create quotations'),
('quotation', 'read', 'View quotations'),
-- ... more permissions
```

### 5. Role_Permissions

Many-to-many relationship between roles and permissions.

```sql
CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

### 6. User_Roles

Many-to-many relationship between users and roles.

```sql
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

---

## Accounting Module Tables

### 7. Chart_of_Accounts

Accounting chart of accounts.

```sql
CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    parent_account_id UUID REFERENCES chart_of_accounts(id),
    
    -- Accounting properties
    is_active BOOLEAN DEFAULT TRUE,
    is_system_account BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_chart_of_accounts_company_code UNIQUE (company_id, account_code),
    CONSTRAINT ck_chart_of_accounts_type CHECK (account_type IN ('asset', 'liability', 'equity', 'revenue', 'expense'))
);

CREATE INDEX idx_chart_of_accounts_company_id ON chart_of_accounts(company_id);
CREATE INDEX idx_chart_of_accounts_parent_id ON chart_of_accounts(parent_account_id);
```

### 8. Customers

Customer/Client information.

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identity
    customer_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(50),
    
    -- Classification
    customer_type VARCHAR(50),
    industry VARCHAR(100),
    segment VARCHAR(50),
    
    -- Address (billing)
    billing_address_line1 VARCHAR(255),
    billing_address_line2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(100),
    billing_postal_code VARCHAR(20),
    billing_country VARCHAR(2),
    
    -- Address (shipping)
    shipping_address_line1 VARCHAR(255),
    shipping_address_line2 VARCHAR(255),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_country VARCHAR(2),
    
    -- Contact
    primary_contact_name VARCHAR(200),
    primary_email VARCHAR(255),
    primary_phone VARCHAR(50),
    website VARCHAR(255),
    
    -- Financial
    credit_limit DECIMAL(15, 2),
    payment_terms VARCHAR(50),
    currency_code VARCHAR(3) DEFAULT 'USD',
    tax_exempt BOOLEAN DEFAULT FALSE,
    tax_rate DECIMAL(5, 4),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Analytics
    lifetime_value DECIMAL(15, 2) DEFAULT 0,
    last_order_date DATE,
    total_orders INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_customers_company_code UNIQUE (company_id, customer_code),
    CONSTRAINT ck_customers_status CHECK (status IN ('active', 'inactive', 'prospect', 'lead'))
);

CREATE INDEX idx_customers_company_id ON customers(company_id);
CREATE INDEX idx_customers_code ON customers(customer_code);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_customers_deleted_at ON customers(deleted_at);
```

### 9. Suppliers

Supplier/Vendor information.

```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identity
    supplier_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(50),
    
    -- Classification
    supplier_type VARCHAR(50),
    category VARCHAR(100),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2),
    
    -- Contact
    primary_contact_name VARCHAR(200),
    primary_email VARCHAR(255),
    primary_phone VARCHAR(50),
    website VARCHAR(255),
    
    -- Financial
    payment_terms VARCHAR(50),
    currency_code VARCHAR(3) DEFAULT 'USD',
    tax_id_number VARCHAR(100),
    
    -- Performance
    on_time_delivery_rate DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),
    average_rating DECIMAL(3, 2),
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(15, 2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Risk
    risk_score INTEGER,
    risk_level VARCHAR(20),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_suppliers_company_code UNIQUE (company_id, supplier_code),
    CONSTRAINT ck_suppliers_status CHECK (status IN ('active', 'inactive', 'pending', 'blacklisted'))
);

CREATE INDEX idx_suppliers_company_id ON suppliers(company_id);
CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_status ON suppliers(status);
```

### 10. Invoices

Sales invoices.

```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    invoice_number VARCHAR(100) NOT NULL,
    invoice_type VARCHAR(20) DEFAULT 'standard',
    
    -- Relationships
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID, -- Reference to production job
    quotation_id UUID, -- Reference to quotation
    
    -- Dates
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    payment_date DATE,
    
    -- Financial
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    balance_amount DECIMAL(15, 2) NOT NULL,
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10, 6) DEFAULT 1,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Payment
    payment_terms VARCHAR(50),
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    
    -- Additional
    notes TEXT,
    internal_notes TEXT,
    reference_number VARCHAR(255),
    
    -- Approval
    approval_status VARCHAR(20),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_invoices_company_number UNIQUE (company_id, invoice_number),
    CONSTRAINT ck_invoices_type CHECK (invoice_type IN ('standard', 'proforma', 'credit', 'debit')),
    CONSTRAINT ck_invoices_status CHECK (status IN ('draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'cancelled'))
);

CREATE INDEX idx_invoices_company_id ON invoices(company_id);
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_job_id ON invoices(job_id);
```

### 11. Invoice_Line_Items

Invoice line items.

```sql
CREATE TABLE invoice_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    
    -- Product/Service
    product_code VARCHAR(100),
    product_name VARCHAR(255),
    
    -- Quantity & Pricing
    quantity DECIMAL(10, 3) NOT NULL,
    unit_price DECIMAL(15, 4) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    
    -- Tax
    tax_rate DECIMAL(5, 4) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    
    -- Reference
    job_id UUID,
    material_id UUID,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_invoice_line_items_invoice_line UNIQUE (invoice_id, line_number)
);

CREATE INDEX idx_invoice_line_items_invoice_id ON invoice_line_items(invoice_id);
CREATE INDEX idx_invoice_line_items_job_id ON invoice_line_items(job_id);
```

### 12. Payments

Payment records.

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    payment_number VARCHAR(100) NOT NULL,
    payment_type VARCHAR(20) NOT NULL,
    
    -- Relationships
    customer_id UUID REFERENCES customers(id),
    supplier_id UUID REFERENCES suppliers(id),
    
    -- Financial
    amount DECIMAL(15, 2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10, 6) DEFAULT 1,
    
    -- Payment Details
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_reference VARCHAR(255),
    bank_account_id UUID,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Additional
    notes TEXT,
    receipt_url TEXT,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_payments_company_number UNIQUE (company_id, payment_number),
    CONSTRAINT ck_payments_type CHECK (payment_type IN ('receipt', 'payment')),
    CONSTRAINT ck_payments_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_payments_company_id ON payments(company_id);
CREATE INDEX idx_payments_customer_id ON payments(customer_id);
CREATE INDEX idx_payments_supplier_id ON payments(supplier_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_status ON payments(status);
```

### 13. Payment_Allocations

Payment allocation to invoices/bills.

```sql
CREATE TABLE payment_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    
    invoice_id UUID REFERENCES invoices(id),
    bill_id UUID, -- Reference to vendor bills
    
    allocated_amount DECIMAL(15, 2) NOT NULL,
    allocation_date DATE NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_payment_allocations_reference CHECK (
        (invoice_id IS NOT NULL AND bill_id IS NULL) OR
        (invoice_id IS NULL AND bill_id IS NOT NULL)
    )
);

CREATE INDEX idx_payment_allocations_payment_id ON payment_allocations(payment_id);
CREATE INDEX idx_payment_allocations_invoice_id ON payment_allocations(invoice_id);
```

### 14. Bills

Vendor bills (Accounts Payable).

```sql
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    bill_number VARCHAR(100) NOT NULL,
    vendor_invoice_number VARCHAR(255),
    
    -- Relationships
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    purchase_order_id UUID,
    
    -- Dates
    bill_date DATE NOT NULL,
    due_date DATE NOT NULL,
    payment_date DATE,
    
    -- Financial
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    balance_amount DECIMAL(15, 2) NOT NULL,
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    approval_status VARCHAR(20),
    
    -- Additional
    notes TEXT,
    attachment_url TEXT,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_bills_company_number UNIQUE (company_id, bill_number),
    CONSTRAINT ck_bills_status CHECK (status IN ('draft', 'pending', 'approved', 'partial', 'paid', 'overdue', 'cancelled'))
);

CREATE INDEX idx_bills_company_id ON bills(company_id);
CREATE INDEX idx_bills_supplier_id ON bills(supplier_id);
CREATE INDEX idx_bills_due_date ON bills(due_date);
CREATE INDEX idx_bills_status ON bills(status);
```

### 15. Documents

Generic document storage for OCR and document management.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    document_type VARCHAR(50) NOT NULL,
    document_category VARCHAR(50),
    
    -- Reference
    reference_type VARCHAR(50), -- 'invoice', 'receipt', 'po', 'do', etc.
    reference_id UUID,
    
    -- File Information
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),
    
    -- OCR Processing
    ocr_status VARCHAR(20) DEFAULT 'pending',
    ocr_processed_at TIMESTAMP,
    ocr_confidence_score DECIMAL(5, 2),
    extracted_data JSONB,
    
    -- Validation
    validation_status VARCHAR(20),
    validation_errors JSONB,
    
    -- Metadata
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_documents_type CHECK (document_type IN ('invoice', 'receipt', 'purchase_order', 'delivery_order', 'quotation', 'contract', 'other')),
    CONSTRAINT ck_documents_ocr_status CHECK (ocr_status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_documents_company_id ON documents(company_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_reference ON documents(reference_type, reference_id);
CREATE INDEX idx_documents_ocr_status ON documents(ocr_status);
```

### 16. Transaction_Matching

Three-way matching records.

```sql
CREATE TABLE transaction_matching (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- References
    purchase_order_id UUID,
    delivery_order_id UUID,
    invoice_id UUID,
    bill_id UUID,
    
    -- Matching Status
    match_type VARCHAR(20), -- 'two_way', 'three_way'
    match_status VARCHAR(20) DEFAULT 'pending',
    match_confidence_score DECIMAL(5, 2),
    
    -- Variances
    amount_variance DECIMAL(15, 2),
    quantity_variance DECIMAL(10, 3),
    date_variance INTEGER, -- days
    
    -- Tolerance
    tolerance_threshold DECIMAL(5, 2),
    within_tolerance BOOLEAN,
    
    -- Exceptions
    exception_reason TEXT,
    exception_resolved BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    matched_at TIMESTAMP,
    matched_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_transaction_matching_type CHECK (match_type IN ('two_way', 'three_way')),
    CONSTRAINT ck_transaction_matching_status CHECK (match_status IN ('pending', 'matched', 'partial', 'exception', 'resolved'))
);

CREATE INDEX idx_transaction_matching_company_id ON transaction_matching(company_id);
CREATE INDEX idx_transaction_matching_po_id ON transaction_matching(purchase_order_id);
CREATE INDEX idx_transaction_matching_status ON transaction_matching(match_status);
```

---

## Purchasing Module Tables

### 17. Materials

Material/Product master data.

```sql
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    material_code VARCHAR(100) NOT NULL,
    material_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Classification
    category VARCHAR(100),
    subcategory VARCHAR(100),
    material_type VARCHAR(50), -- 'raw', 'component', 'finished_good', 'consumable'
    
    -- Specifications
    unit_of_measure VARCHAR(20) NOT NULL,
    weight DECIMAL(10, 3),
    dimensions VARCHAR(100),
    specifications JSONB,
    
    -- Inventory
    current_stock DECIMAL(10, 3) DEFAULT 0,
    reorder_point DECIMAL(10, 3) DEFAULT 0,
    reorder_quantity DECIMAL(10, 3),
    safety_stock DECIMAL(10, 3) DEFAULT 0,
    max_stock DECIMAL(10, 3),
    
    -- Pricing
    standard_cost DECIMAL(15, 4),
    average_cost DECIMAL(15, 4),
    last_purchase_price DECIMAL(15, 4),
    
    -- Supplier
    preferred_supplier_id UUID REFERENCES suppliers(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Analytics
    abc_category VARCHAR(1), -- 'A', 'B', 'C'
    turnover_rate DECIMAL(10, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT uk_materials_company_code UNIQUE (company_id, material_code),
    CONSTRAINT ck_materials_type CHECK (material_type IN ('raw', 'component', 'finished_good', 'consumable', 'tooling')),
    CONSTRAINT ck_materials_status CHECK (status IN ('active', 'inactive', 'obsolete'))
);

CREATE INDEX idx_materials_company_id ON materials(company_id);
CREATE INDEX idx_materials_code ON materials(material_code);
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_materials_status ON materials(status);
CREATE INDEX idx_materials_current_stock ON materials(current_stock);
```

### 18. Inventory_Transactions

Inventory movement transactions.

```sql
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Reference
    material_id UUID NOT NULL REFERENCES materials(id),
    transaction_type VARCHAR(50) NOT NULL,
    
    -- Reference Documents
    purchase_order_id UUID,
    delivery_id UUID,
    job_id UUID,
    adjustment_reason_id UUID,
    
    -- Transaction Details
    quantity DECIMAL(10, 3) NOT NULL,
    unit_cost DECIMAL(15, 4),
    total_cost DECIMAL(15, 2),
    
    -- Inventory Levels
    quantity_before DECIMAL(10, 3) NOT NULL,
    quantity_after DECIMAL(10, 3) NOT NULL,
    
    -- Location
    warehouse_id UUID,
    location_code VARCHAR(100),
    
    -- Additional
    reference_number VARCHAR(255),
    notes TEXT,
    
    -- Metadata
    transaction_date TIMESTAMP NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_inventory_transactions_type CHECK (transaction_type IN ('receipt', 'issue', 'transfer', 'adjustment', 'return', 'write_off'))
);

CREATE INDEX idx_inventory_transactions_company_id ON inventory_transactions(company_id);
CREATE INDEX idx_inventory_transactions_material_id ON inventory_transactions(material_id);
CREATE INDEX idx_inventory_transactions_type ON inventory_transactions(transaction_type);
CREATE INDEX idx_inventory_transactions_date ON inventory_transactions(transaction_date);
```

### 19. Purchase_Orders

Purchase orders.

```sql
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    po_number VARCHAR(100) NOT NULL,
    po_type VARCHAR(20) DEFAULT 'standard',
    
    -- Relationships
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    requested_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    
    -- Dates
    po_date DATE NOT NULL,
    required_date DATE,
    expected_delivery_date DATE,
    
    -- Financial
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(10, 6) DEFAULT 1,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    approval_status VARCHAR(20),
    
    -- Shipping
    shipping_address_id UUID,
    shipping_method VARCHAR(50),
    shipping_terms VARCHAR(50),
    
    -- Terms
    payment_terms VARCHAR(50),
    delivery_terms VARCHAR(50),
    
    -- Additional
    notes TEXT,
    internal_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    
    CONSTRAINT uk_purchase_orders_company_number UNIQUE (company_id, po_number),
    CONSTRAINT ck_purchase_orders_type CHECK (po_type IN ('standard', 'blanket', 'contract')),
    CONSTRAINT ck_purchase_orders_status CHECK (status IN ('draft', 'pending', 'sent', 'acknowledged', 'partially_received', 'received', 'closed', 'cancelled'))
);

CREATE INDEX idx_purchase_orders_company_id ON purchase_orders(company_id);
CREATE INDEX idx_purchase_orders_supplier_id ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_number ON purchase_orders(po_number);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_date ON purchase_orders(po_date);
```

### 20. Purchase_Order_Line_Items

PO line items.

```sql
CREATE TABLE purchase_order_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    
    line_number INTEGER NOT NULL,
    
    -- Material
    material_id UUID REFERENCES materials(id),
    material_code VARCHAR(100),
    material_description TEXT NOT NULL,
    
    -- Quantity & Pricing
    quantity_ordered DECIMAL(10, 3) NOT NULL,
    quantity_received DECIMAL(10, 3) DEFAULT 0,
    quantity_pending DECIMAL(10, 3) NOT NULL,
    
    unit_price DECIMAL(15, 4) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    
    -- Delivery
    expected_delivery_date DATE,
    received_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_po_line_items_po_line UNIQUE (purchase_order_id, line_number),
    CONSTRAINT ck_po_line_items_status CHECK (status IN ('pending', 'partial', 'received', 'cancelled'))
);

CREATE INDEX idx_po_line_items_po_id ON purchase_order_line_items(purchase_order_id);
CREATE INDEX idx_po_line_items_material_id ON purchase_order_line_items(material_id);
```

### 21. Deliveries

Delivery/Goods Receipt records.

```sql
CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    delivery_number VARCHAR(100) NOT NULL,
    
    -- Relationships
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id),
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    
    -- Dates
    delivery_date DATE NOT NULL,
    received_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    quality_status VARCHAR(20),
    
    -- Shipping
    carrier_name VARCHAR(100),
    tracking_number VARCHAR(255),
    shipping_cost DECIMAL(15, 2),
    
    -- Additional
    notes TEXT,
    inspection_notes TEXT,
    
    -- Metadata
    received_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_deliveries_company_number UNIQUE (company_id, delivery_number),
    CONSTRAINT ck_deliveries_status CHECK (status IN ('pending', 'in_transit', 'received', 'partial', 'completed', 'cancelled')),
    CONSTRAINT ck_deliveries_quality_status CHECK (quality_status IN ('pending', 'passed', 'failed', 'conditional'))
);

CREATE INDEX idx_deliveries_company_id ON deliveries(company_id);
CREATE INDEX idx_deliveries_po_id ON deliveries(purchase_order_id);
CREATE INDEX idx_deliveries_supplier_id ON deliveries(supplier_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
```

### 22. Delivery_Line_Items

Delivery line items.

```sql
CREATE TABLE delivery_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    po_line_item_id UUID REFERENCES purchase_order_line_items(id),
    
    -- Material
    material_id UUID NOT NULL REFERENCES materials(id),
    material_code VARCHAR(100),
    material_description TEXT,
    
    -- Quantity
    quantity_received DECIMAL(10, 3) NOT NULL,
    quantity_accepted DECIMAL(10, 3),
    quantity_rejected DECIMAL(10, 3) DEFAULT 0,
    
    -- Quality
    quality_status VARCHAR(20),
    inspection_result TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_delivery_line_items_delivery_id ON delivery_line_items(delivery_id);
CREATE INDEX idx_delivery_line_items_material_id ON delivery_line_items(material_id);
```

### 23. Demand_Forecasts

Demand forecasting data.

```sql
CREATE TABLE demand_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Material
    material_id UUID NOT NULL REFERENCES materials(id),
    
    -- Forecast Period
    forecast_date DATE NOT NULL,
    forecast_horizon VARCHAR(20), -- 'weekly', 'monthly', 'quarterly'
    
    -- Forecast Data
    forecasted_quantity DECIMAL(10, 3) NOT NULL,
    confidence_interval_lower DECIMAL(10, 3),
    confidence_interval_upper DECIMAL(10, 3),
    confidence_score DECIMAL(5, 2),
    
    -- Model Information
    forecast_model VARCHAR(50),
    model_version VARCHAR(20),
    
    -- Actuals (for accuracy tracking)
    actual_quantity DECIMAL(10, 3),
    forecast_accuracy DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_demand_forecasts_horizon CHECK (forecast_horizon IN ('weekly', 'monthly', 'quarterly', 'yearly'))
);

CREATE INDEX idx_demand_forecasts_company_id ON demand_forecasts(company_id);
CREATE INDEX idx_demand_forecasts_material_id ON demand_forecasts(material_id);
CREATE INDEX idx_demand_forecasts_date ON demand_forecasts(forecast_date);
```

---

## Sales Module Tables

### 24. Quotations

Quotations/Quotes.

```sql
CREATE TABLE quotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    quotation_number VARCHAR(100) NOT NULL,
    
    -- Relationships
    customer_id UUID NOT NULL REFERENCES customers(id),
    opportunity_id UUID,
    
    -- Dates
    quotation_date DATE NOT NULL,
    valid_until DATE NOT NULL,
    expiration_date DATE,
    
    -- Financial
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Pricing
    pricing_method VARCHAR(50),
    margin_percent DECIMAL(5, 2),
    
    -- Terms
    payment_terms VARCHAR(50),
    delivery_terms VARCHAR(50),
    lead_time_days INTEGER,
    
    -- Additional
    notes TEXT,
    customer_notes TEXT,
    
    -- Analytics
    viewed_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_quotations_company_number UNIQUE (company_id, quotation_number),
    CONSTRAINT ck_quotations_status CHECK (status IN ('draft', 'sent', 'viewed', 'accepted', 'rejected', 'expired', 'converted'))
);

CREATE INDEX idx_quotations_company_id ON quotations(company_id);
CREATE INDEX idx_quotations_customer_id ON quotations(customer_id);
CREATE INDEX idx_quotations_number ON quotations(quotation_number);
CREATE INDEX idx_quotations_status ON quotations(status);
CREATE INDEX idx_quotations_date ON quotations(quotation_date);
```

### 25. Quotation_Line_Items

Quotation line items.

```sql
CREATE TABLE quotation_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_id UUID NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
    
    line_number INTEGER NOT NULL,
    
    -- Product/Service
    product_code VARCHAR(100),
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Specifications
    specifications JSONB,
    machining_requirements TEXT,
    
    -- Quantity & Pricing
    quantity DECIMAL(10, 3) NOT NULL,
    unit_price DECIMAL(15, 4) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    
    -- Time Estimation
    estimated_hours DECIMAL(10, 2),
    setup_hours DECIMAL(10, 2),
    
    -- Material
    material_cost DECIMAL(15, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_quotation_line_items_quotation_line UNIQUE (quotation_id, line_number)
);

CREATE INDEX idx_quotation_line_items_quotation_id ON quotation_line_items(quotation_id);
```

### 26. Sales_Opportunities

Sales opportunities/pipeline.

```sql
CREATE TABLE sales_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    opportunity_name VARCHAR(255) NOT NULL,
    
    -- Relationships
    customer_id UUID NOT NULL REFERENCES customers(id),
    assigned_to UUID REFERENCES users(id),
    
    -- Financial
    estimated_value DECIMAL(15, 2),
    weighted_value DECIMAL(15, 2),
    actual_value DECIMAL(15, 2),
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    
    -- Pipeline
    stage VARCHAR(50) NOT NULL,
    win_probability DECIMAL(5, 2) DEFAULT 0,
    
    -- Dates
    expected_close_date DATE,
    actual_close_date DATE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'open',
    
    -- Source
    source VARCHAR(50),
    
    -- Additional
    description TEXT,
    next_step TEXT,
    
    -- Analytics
    days_in_stage INTEGER,
    total_days INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    
    CONSTRAINT ck_sales_opportunities_status CHECK (status IN ('open', 'won', 'lost', 'abandoned'))
);

CREATE INDEX idx_sales_opportunities_company_id ON sales_opportunities(company_id);
CREATE INDEX idx_sales_opportunities_customer_id ON sales_opportunities(customer_id);
CREATE INDEX idx_sales_opportunities_assigned_to ON sales_opportunities(assigned_to);
CREATE INDEX idx_sales_opportunities_stage ON sales_opportunities(stage);
CREATE INDEX idx_sales_opportunities_status ON sales_opportunities(status);
```

### 27. Orders

Sales orders.

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Identification
    order_number VARCHAR(100) NOT NULL,
    
    -- Relationships
    customer_id UUID NOT NULL REFERENCES customers(id),
    quotation_id UUID REFERENCES quotations(id),
    opportunity_id UUID REFERENCES sales_opportunities(id),
    
    -- Dates
    order_date DATE NOT NULL,
    required_date DATE,
    delivery_date DATE,
    
    -- Financial
    subtotal DECIMAL(15, 2) NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) NOT NULL,
    
    currency_code VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Shipping
    shipping_address_id UUID,
    shipping_method VARCHAR(50),
    
    -- Payment
    payment_terms VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    
    -- Additional
    notes TEXT,
    customer_po_number VARCHAR(255),
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_orders_company_number UNIQUE (company_id, order_number),
    CONSTRAINT ck_orders_status CHECK (status IN ('pending', 'confirmed', 'in_production', 'completed', 'shipped', 'delivered', 'cancelled')),
    CONSTRAINT ck_orders_payment_status CHECK (payment_status IN ('pending', 'partial', 'paid', 'overdue'))
);

CREATE INDEX idx_orders_company_id ON orders(company_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(order_date);
```

---

## Email/Chatbot Module Tables

### 28. Email_Accounts

Email account configurations.

```sql
CREATE TABLE email_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Account Information
    account_name VARCHAR(255) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    
    -- Connection
    provider VARCHAR(50), -- 'gmail', 'outlook', 'imap', 'pop3'
    connection_type VARCHAR(20), -- 'imap', 'pop3', 'api'
    
    -- Credentials (encrypted)
    encrypted_credentials TEXT,
    
    -- Settings
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    
    -- Sync
    last_sync_at TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_email_accounts_company_email UNIQUE (company_id, email_address)
);

CREATE INDEX idx_email_accounts_company_id ON email_accounts(company_id);
CREATE INDEX idx_email_accounts_active ON email_accounts(is_active);
```

### 29. Emails

Email messages.

```sql
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email_account_id UUID NOT NULL REFERENCES email_accounts(id),
    
    -- Email Headers
    message_id VARCHAR(255) UNIQUE,
    thread_id VARCHAR(255),
    in_reply_to VARCHAR(255),
    references_header TEXT,
    
    -- Participants
    from_email VARCHAR(255) NOT NULL,
    from_name VARCHAR(255),
    to_emails TEXT[] NOT NULL,
    cc_emails TEXT[],
    bcc_emails TEXT[],
    
    -- Content
    subject VARCHAR(500),
    body_text TEXT,
    body_html TEXT,
    
    -- Classification
    category VARCHAR(50), -- 'inquiry', 'order', 'complaint', 'invoice', 'general'
    priority VARCHAR(10) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    priority_score DECIMAL(5, 2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'new',
    is_read BOOLEAN DEFAULT FALSE,
    is_spam BOOLEAN DEFAULT FALSE,
    
    -- Sentiment
    sentiment_score DECIMAL(5, 2),
    sentiment_label VARCHAR(20),
    
    -- Relationship
    customer_id UUID REFERENCES customers(id),
    supplier_id UUID REFERENCES suppliers(id),
    related_document_type VARCHAR(50),
    related_document_id UUID,
    
    -- Attachments
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_count INTEGER DEFAULT 0,
    
    -- Response
    auto_responded BOOLEAN DEFAULT FALSE,
    response_id UUID,
    escalated BOOLEAN DEFAULT FALSE,
    escalated_to UUID REFERENCES users(id),
    
    -- Dates
    received_at TIMESTAMP NOT NULL,
    read_at TIMESTAMP,
    responded_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_emails_category CHECK (category IN ('inquiry', 'order', 'complaint', 'invoice', 'quotation', 'payment', 'general')),
    CONSTRAINT ck_emails_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CONSTRAINT ck_emails_status CHECK (status IN ('new', 'read', 'replied', 'forwarded', 'archived', 'deleted'))
);

CREATE INDEX idx_emails_company_id ON emails(company_id);
CREATE INDEX idx_emails_account_id ON emails(email_account_id);
CREATE INDEX idx_emails_thread_id ON emails(thread_id);
CREATE INDEX idx_emails_from_email ON emails(from_email);
CREATE INDEX idx_emails_customer_id ON emails(customer_id);
CREATE INDEX idx_emails_category ON emails(category);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_received_at ON emails(received_at);
CREATE INDEX idx_emails_priority_score ON emails(priority_score);
```

### 30. Email_Attachments

Email attachments.

```sql
CREATE TABLE email_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    
    -- File Information
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    
    -- Processing
    ocr_processed BOOLEAN DEFAULT FALSE,
    extracted_data JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_attachments_email_id ON email_attachments(email_id);
```

### 31. Conversations

Chatbot conversations.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Participant
    customer_id UUID REFERENCES customers(id),
    participant_email VARCHAR(255),
    participant_name VARCHAR(255),
    participant_phone VARCHAR(50),
    
    -- Channel
    channel VARCHAR(50) NOT NULL, -- 'web_chat', 'email', 'sms', 'whatsapp'
    channel_identifier VARCHAR(255),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_resolved BOOLEAN DEFAULT FALSE,
    
    -- Classification
    intent VARCHAR(100),
    category VARCHAR(50),
    
    -- Handoff
    escalated_to_human BOOLEAN DEFAULT FALSE,
    assigned_to UUID REFERENCES users(id),
    
    -- Analytics
    message_count INTEGER DEFAULT 0,
    avg_response_time_seconds INTEGER,
    satisfaction_score INTEGER,
    
    -- Dates
    started_at TIMESTAMP NOT NULL,
    last_message_at TIMESTAMP,
    ended_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_conversations_channel CHECK (channel IN ('web_chat', 'email', 'sms', 'whatsapp', 'facebook', 'voice')),
    CONSTRAINT ck_conversations_status CHECK (status IN ('active', 'waiting', 'resolved', 'abandoned', 'escalated'))
);

CREATE INDEX idx_conversations_company_id ON conversations(company_id);
CREATE INDEX idx_conversations_customer_id ON conversations(customer_id);
CREATE INDEX idx_conversations_channel ON conversations(channel);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
```

### 32. Messages

Chatbot messages.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message Content
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text', -- 'text', 'image', 'file', 'button', 'card'
    
    -- Direction
    direction VARCHAR(10) NOT NULL, -- 'inbound', 'outbound'
    
    -- Sender
    sender_type VARCHAR(20) NOT NULL, -- 'user', 'bot', 'agent'
    sender_id UUID, -- user_id if sender_type is 'user' or 'agent'
    
    -- AI Processing
    intent VARCHAR(100),
    entities JSONB,
    confidence_score DECIMAL(5, 2),
    
    -- Response
    is_auto_generated BOOLEAN DEFAULT FALSE,
    template_used VARCHAR(100),
    
    -- Metadata
    sent_at TIMESTAMP NOT NULL,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_messages_type CHECK (message_type IN ('text', 'image', 'file', 'button', 'card', 'quick_reply')),
    CONSTRAINT ck_messages_direction CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT ck_messages_sender_type CHECK (sender_type IN ('user', 'bot', 'agent'))
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_direction ON messages(direction);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
```

### 33. Knowledge_Base

Knowledge base articles.

```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_html TEXT,
    summary TEXT,
    
    -- Classification
    category VARCHAR(100),
    tags TEXT[],
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    is_published BOOLEAN DEFAULT FALSE,
    
    -- Usage
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    
    -- Search
    search_vector tsvector,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    
    CONSTRAINT ck_knowledge_base_status CHECK (status IN ('draft', 'published', 'archived'))
);

CREATE INDEX idx_knowledge_base_company_id ON knowledge_base(company_id);
CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_base_status ON knowledge_base(status);
CREATE INDEX idx_knowledge_base_search ON knowledge_base USING gin(search_vector);
```

---

## Audit & Logging Tables

### 34. Audit_Logs

Comprehensive audit trail.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    
    -- Action Details
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    
    -- User
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    
    -- Status
    status VARCHAR(20), -- 'success', 'failure', 'error'
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_company_id ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 35. System_Events

System-wide events for integration.

```sql
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    
    -- Event Details
    event_type VARCHAR(100) NOT NULL,
    event_source VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    
    -- Payload
    payload JSONB NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    processed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_events_company_id ON system_events(company_id);
CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_status ON system_events(status);
CREATE INDEX idx_system_events_created_at ON system_events(created_at);
```

---

## Indexes Summary

### Performance Indexes
- Foreign key indexes on all foreign key columns
- Composite indexes for common query patterns
- Full-text search indexes (GIN indexes for JSONB, tsvector)
- Partial indexes for filtered queries (e.g., active records only)

### Maintenance
- Regular VACUUM and ANALYZE
- Index maintenance scheduling
- Query performance monitoring

---

## Database Views

### Useful Views for Reporting

```sql
-- Accounts Receivable Aging View
CREATE VIEW v_accounts_receivable_aging AS
SELECT 
    i.company_id,
    i.customer_id,
    c.name AS customer_name,
    i.invoice_number,
    i.invoice_date,
    i.due_date,
    i.total_amount,
    i.balance_amount,
    CASE
        WHEN i.due_date >= CURRENT_DATE THEN i.balance_amount
        ELSE 0
    END AS current_amount,
    CASE
        WHEN i.due_date < CURRENT_DATE AND i.due_date >= CURRENT_DATE - INTERVAL '30 days' 
        THEN i.balance_amount
        ELSE 0
    END AS days_30,
    CASE
        WHEN i.due_date < CURRENT_DATE - INTERVAL '30 days' 
        AND i.due_date >= CURRENT_DATE - INTERVAL '60 days'
        THEN i.balance_amount
        ELSE 0
    END AS days_60,
    CASE
        WHEN i.due_date < CURRENT_DATE - INTERVAL '60 days'
        THEN i.balance_amount
        ELSE 0
    END AS days_90_plus
FROM invoices i
JOIN customers c ON i.customer_id = c.id
WHERE i.status NOT IN ('paid', 'cancelled')
AND i.balance_amount > 0;

-- Inventory Summary View
CREATE VIEW v_inventory_summary AS
SELECT
    m.company_id,
    m.id AS material_id,
    m.material_code,
    m.material_name,
    m.current_stock,
    m.reorder_point,
    m.safety_stock,
    CASE 
        WHEN m.current_stock <= m.reorder_point THEN 'low'
        WHEN m.current_stock <= m.reorder_point + m.safety_stock THEN 'warning'
        ELSE 'ok'
    END AS stock_status,
    m.standard_cost,
    (m.current_stock * m.standard_cost) AS inventory_value
FROM materials m
WHERE m.status = 'active'
AND m.deleted_at IS NULL;
```

---

## Stored Procedures & Functions

### Example: Calculate Invoice Balance

```sql
CREATE OR REPLACE FUNCTION calculate_invoice_balance(invoice_uuid UUID)
RETURNS DECIMAL(15, 2) AS $$
DECLARE
    total_paid DECIMAL(15, 2);
    invoice_total DECIMAL(15, 2);
BEGIN
    -- Calculate total payments allocated to this invoice
    SELECT COALESCE(SUM(pa.allocated_amount), 0)
    INTO total_paid
    FROM payment_allocations pa
    WHERE pa.invoice_id = invoice_uuid;
    
    -- Get invoice total
    SELECT total_amount
    INTO invoice_total
    FROM invoices
    WHERE id = invoice_uuid;
    
    -- Return balance
    RETURN invoice_total - total_paid;
END;
$$ LANGUAGE plpgsql;
```

---

## Data Retention & Archiving

### Retention Policies
- **Active Data:** Keep all active records indefinitely
- **Deleted Records:** Soft delete with 90-day retention before hard delete
- **Audit Logs:** 7 years retention for compliance
- **System Events:** 90 days retention

### Archiving Strategy
- Archive old transactions to separate tables
- Monthly archive process
- Compressed storage for archived data

---

## Security Considerations

1. **Row-Level Security (RLS):** Implement RLS policies for multi-tenancy
2. **Data Encryption:** Encrypt sensitive columns (credit card numbers, SSN, etc.)
3. **Access Control:** Database-level permissions aligned with application RBAC
4. **Audit Trail:** Comprehensive logging of all data access and changes
5. **Backup Strategy:** Daily incremental, weekly full backups
6. **Disaster Recovery:** Point-in-time recovery capability

---

## Migration Strategy

1. **Version Control:** Use database migration tools (Liquibase, Flyway)
2. **Zero-Downtime Migrations:** Design migrations for online deployment
3. **Rollback Plan:** Maintain rollback scripts for each migration
4. **Testing:** Test migrations on staging before production

---

**Document Control:**
- **Author:** Database Architecture Team
- **Last Review:** 2024
- **Database Version:** 1.0


