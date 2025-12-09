# API Specification Documentation
## Unified AI Business Assistant for CNC Factory

**Version:** 1.0  
**API Base URL:** `https://api.unified-ai-assistant.com/v1`  
**Authentication:** Bearer Token (JWT)  
**Last Updated:** 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Patterns](#common-patterns)
4. [Account Management APIs](#account-management-apis)
5. [Accounting Module APIs](#accounting-module-apis)
6. [Purchasing Module APIs](#purchasing-module-apis)
7. [Sales Module APIs](#sales-module-apis)
8. [Email/Chatbot Module APIs](#emailchatbot-module-apis)
9. [Dashboard & Analytics APIs](#dashboard--analytics-apis)
10. [Webhooks](#webhooks)
11. [Rate Limiting](#rate-limiting)
12. [Error Handling](#error-handling)

---

## Overview

### API Architecture

The API follows RESTful principles with the following characteristics:

- **RESTful Design:** Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **JSON Format:** All requests and responses use JSON
- **Versioning:** URL-based versioning (`/v1/`)
- **Pagination:** Cursor-based and offset-based pagination
- **Filtering & Sorting:** Query parameter-based
- **Error Handling:** Standardized error response format

### Base URL

```
Production: https://api.unified-ai-assistant.com/v1
Staging: https://staging-api.unified-ai-assistant.com/v1
Development: http://localhost:3000/api/v1
```

### Response Format

All API responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... },
    "request_id": "req_abc123"
  }
}
```

---

## Authentication

### Authentication Methods

#### 1. Bearer Token (JWT)

Most API endpoints require authentication using a JWT Bearer token.

**Request Header:**
```
Authorization: Bearer <jwt_token>
```

#### 2. API Key (Service-to-Service)

For server-to-server communication:

**Request Header:**
```
X-API-Key: <api_key>
```

### Authentication Endpoints

#### POST /auth/login

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_abc123",
    "expires_in": 3600,
    "user": {
      "id": "user_uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "roles": ["admin", "accountant"]
    }
  }
}
```

#### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_abc123"
}
```

#### POST /auth/logout

Invalidate current session.

---

## Common Patterns

### Pagination

**Offset-based Pagination:**

```
GET /api/v1/invoices?page=1&limit=50
```

**Response:**
```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 1250,
      "total_pages": 25
    }
  }
}
```

**Cursor-based Pagination (for large datasets):**

```
GET /api/v1/invoices?cursor=eyJpZCI6IjEyMyJ9&limit=50
```

### Filtering

```
GET /api/v1/invoices?status=paid&customer_id=abc123&date_from=2024-01-01&date_to=2024-12-31
```

### Sorting

```
GET /api/v1/invoices?sort=invoice_date&order=desc
```

Multiple fields:
```
GET /api/v1/invoices?sort=status,invoice_date&order=asc,desc
```

### Field Selection

```
GET /api/v1/invoices?fields=id,invoice_number,total_amount,status
```

### Search

```
GET /api/v1/invoices?search=INV-2024&search_fields=invoice_number,customer_name
```

---

## Account Management APIs

### Users

#### GET /users

Get list of users.

**Query Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `search` (string): Search term
- `role` (string): Filter by role
- `status` (string): Filter by status

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "user_uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "display_name": "John Doe",
      "roles": ["admin"],
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": { "pagination": { ... } }
}
```

#### GET /users/:id

Get user details.

#### POST /users

Create new user.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "roles": ["accountant"],
  "status": "active"
}
```

#### PUT /users/:id

Update user.

#### DELETE /users/:id

Delete user (soft delete).

---

## Accounting Module APIs

### Invoices

#### GET /invoices

Get list of invoices.

**Query Parameters:**
- `status` (string): Filter by status
- `customer_id` (uuid): Filter by customer
- `date_from` (date): Start date
- `date_to` (date): End date
- `min_amount` (decimal): Minimum amount
- `max_amount` (decimal): Maximum amount
- `overdue_only` (boolean): Only overdue invoices

**Example:**
```
GET /invoices?status=unpaid&date_from=2024-01-01&overdue_only=true
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "invoice_uuid",
      "invoice_number": "INV-2024-001",
      "customer": {
        "id": "customer_uuid",
        "name": "ABC Company"
      },
      "invoice_date": "2024-01-15",
      "due_date": "2024-02-14",
      "total_amount": 15000.00,
      "paid_amount": 0.00,
      "balance_amount": 15000.00,
      "status": "unpaid",
      "currency_code": "USD",
      "line_items": [
        {
          "description": "CNC Machining Services",
          "quantity": 10,
          "unit_price": 1500.00,
          "line_total": 15000.00
        }
      ],
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "meta": { "pagination": { ... } }
}
```

#### GET /invoices/:id

Get invoice details.

#### POST /invoices

Create new invoice.

**Request Body:**
```json
{
  "customer_id": "customer_uuid",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-14",
  "payment_terms": "Net 30",
  "line_items": [
    {
      "description": "CNC Machining Services",
      "quantity": 10,
      "unit_price": 1500.00,
      "tax_rate": 0.10
    }
  ],
  "notes": "Thank you for your business"
}
```

#### PUT /invoices/:id

Update invoice.

#### POST /invoices/:id/send

Send invoice to customer via email.

#### POST /invoices/:id/mark-paid

Mark invoice as paid.

**Request Body:**
```json
{
  "payment_date": "2024-01-20",
  "payment_method": "bank_transfer",
  "payment_reference": "TXN123456"
}
```

#### GET /invoices/:id/pdf

Generate and download invoice PDF.

### Payments

#### GET /payments

Get list of payments.

**Query Parameters:**
- `type` (string): 'receipt' or 'payment'
- `customer_id` (uuid): Filter by customer
- `supplier_id` (uuid): Filter by supplier
- `date_from` (date): Start date
- `date_to` (date): End date

#### POST /payments

Record a payment.

**Request Body:**
```json
{
  "payment_type": "receipt",
  "customer_id": "customer_uuid",
  "amount": 15000.00,
  "payment_date": "2024-01-20",
  "payment_method": "bank_transfer",
  "payment_reference": "TXN123456",
  "allocations": [
    {
      "invoice_id": "invoice_uuid",
      "amount": 15000.00
    }
  ]
}
```

### Documents

#### POST /documents/upload

Upload document for OCR processing.

**Request:** Multipart form data
- `file` (file): Document file
- `document_type` (string): 'invoice', 'receipt', 'po', etc.
- `reference_id` (uuid): Optional reference ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "document_uuid",
    "document_type": "invoice",
    "file_name": "invoice.pdf",
    "ocr_status": "processing",
    "extracted_data": null
  }
}
```

#### GET /documents/:id

Get document details and extracted data.

#### GET /documents/:id/status

Check OCR processing status.

### Transaction Matching

#### GET /matching/pending

Get pending matching transactions.

#### POST /matching/match

Create a match between documents.

**Request Body:**
```json
{
  "purchase_order_id": "po_uuid",
  "delivery_order_id": "do_uuid",
  "invoice_id": "invoice_uuid",
  "match_type": "three_way",
  "tolerance_threshold": 0.05
}
```

#### GET /matching/:id

Get matching details.

### Financial Reports

#### GET /reports/accounts-receivable-aging

Get AR aging report.

**Query Parameters:**
- `as_of_date` (date): Report date (default: today)
- `customer_id` (uuid): Filter by customer

**Response:**
```json
{
  "success": true,
  "data": {
    "as_of_date": "2024-01-15",
    "summary": {
      "current": 50000.00,
      "days_30": 25000.00,
      "days_60": 15000.00,
      "days_90_plus": 10000.00,
      "total": 100000.00
    },
    "details": [
      {
        "customer_id": "customer_uuid",
        "customer_name": "ABC Company",
        "current": 10000.00,
        "days_30": 5000.00,
        "days_60": 0,
        "days_90_plus": 0,
        "total": 15000.00
      }
    ]
  }
}
```

#### GET /reports/profit-loss

Get Profit & Loss statement.

**Query Parameters:**
- `start_date` (date): Required
- `end_date` (date): Required
- `period` (string): 'monthly', 'quarterly', 'yearly'

#### GET /reports/balance-sheet

Get Balance Sheet.

**Query Parameters:**
- `as_of_date` (date): Required

#### GET /reports/cash-flow

Get Cash Flow statement.

---

## Purchasing Module APIs

### Materials

#### GET /materials

Get list of materials.

**Query Parameters:**
- `category` (string): Filter by category
- `status` (string): Filter by status
- `low_stock_only` (boolean): Only materials below reorder point
- `search` (string): Search term

#### GET /materials/:id

Get material details.

#### POST /materials

Create new material.

**Request Body:**
```json
{
  "material_code": "MAT-001",
  "material_name": "Aluminum 6061",
  "category": "Raw Material",
  "unit_of_measure": "kg",
  "reorder_point": 100.00,
  "reorder_quantity": 500.00,
  "safety_stock": 50.00,
  "standard_cost": 5.50
}
```

#### PUT /materials/:id

Update material.

#### GET /materials/:id/inventory-transactions

Get inventory transaction history.

### Purchase Orders

#### GET /purchase-orders

Get list of purchase orders.

**Query Parameters:**
- `status` (string): Filter by status
- `supplier_id` (uuid): Filter by supplier
- `date_from` (date): Start date
- `date_to` (date): End date

#### GET /purchase-orders/:id

Get PO details.

#### POST /purchase-orders

Create new purchase order.

**Request Body:**
```json
{
  "supplier_id": "supplier_uuid",
  "po_date": "2024-01-15",
  "required_date": "2024-01-30",
  "payment_terms": "Net 30",
  "line_items": [
    {
      "material_id": "material_uuid",
      "quantity": 500.00,
      "unit_price": 5.50,
      "expected_delivery_date": "2024-01-30"
    }
  ],
  "notes": "Urgent order"
}
```

#### POST /purchase-orders/:id/approve

Approve purchase order.

#### POST /purchase-orders/:id/send

Send PO to supplier.

#### POST /purchase-orders/:id/cancel

Cancel purchase order.

### Suppliers

#### GET /suppliers

Get list of suppliers.

#### GET /suppliers/:id

Get supplier details.

#### POST /suppliers

Create new supplier.

**Request Body:**
```json
{
  "supplier_code": "SUP-001",
  "name": "ABC Materials Inc.",
  "primary_email": "contact@abcmaterials.com",
  "primary_phone": "+1-555-0123",
  "address": {
    "line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "payment_terms": "Net 30"
}
```

#### GET /suppliers/:id/performance

Get supplier performance metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "supplier_id": "supplier_uuid",
    "on_time_delivery_rate": 95.5,
    "quality_score": 4.2,
    "average_rating": 4.5,
    "total_orders": 150,
    "total_spent": 250000.00,
    "performance_trend": {
      "last_30_days": {
        "on_time_delivery_rate": 96.0,
        "quality_score": 4.3
      },
      "last_90_days": {
        "on_time_delivery_rate": 94.5,
        "quality_score": 4.1
      }
    }
  }
}
```

### Deliveries

#### GET /deliveries

Get list of deliveries.

#### GET /deliveries/:id

Get delivery details.

#### POST /deliveries

Record goods receipt.

**Request Body:**
```json
{
  "purchase_order_id": "po_uuid",
  "delivery_date": "2024-01-25",
  "line_items": [
    {
      "po_line_item_id": "po_line_uuid",
      "quantity_received": 500.00,
      "quantity_accepted": 495.00,
      "quantity_rejected": 5.00,
      "quality_status": "passed"
    }
  ]
}
```

### Demand Forecasting

#### GET /forecasts/materials/:material_id

Get demand forecast for a material.

**Query Parameters:**
- `horizon` (string): 'weekly', 'monthly', 'quarterly'
- `periods` (integer): Number of periods to forecast

**Response:**
```json
{
  "success": true,
  "data": {
    "material_id": "material_uuid",
    "material_code": "MAT-001",
    "forecast_horizon": "monthly",
    "forecasts": [
      {
        "period": "2024-02",
        "forecasted_quantity": 450.00,
        "confidence_lower": 400.00,
        "confidence_upper": 500.00,
        "confidence_score": 0.85
      },
      {
        "period": "2024-03",
        "forecasted_quantity": 480.00,
        "confidence_lower": 430.00,
        "confidence_upper": 530.00,
        "confidence_score": 0.82
      }
    ],
    "model_info": {
      "model_type": "LSTM",
      "model_version": "1.2.0",
      "accuracy_score": 0.88
    }
  }
}
```

#### POST /forecasts/recalculate

Trigger recalculation of forecasts for all materials or specific materials.

---

## Sales Module APIs

### Customers

#### GET /customers

Get list of customers.

**Query Parameters:**
- `status` (string): Filter by status
- `segment` (string): Filter by segment
- `search` (string): Search term

#### GET /customers/:id

Get customer details.

#### POST /customers

Create new customer.

**Request Body:**
```json
{
  "customer_code": "CUST-001",
  "name": "XYZ Manufacturing",
  "primary_email": "contact@xyz.com",
  "primary_phone": "+1-555-0456",
  "credit_limit": 100000.00,
  "payment_terms": "Net 30",
  "billing_address": {
    "line1": "456 Oak Ave",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90001",
    "country": "US"
  }
}
```

#### GET /customers/:id/intelligence

Get customer intelligence data.

**Response:**
```json
{
  "success": true,
  "data": {
    "customer_id": "customer_uuid",
    "lifetime_value": 250000.00,
    "total_orders": 45,
    "average_order_value": 5555.56,
    "last_order_date": "2024-01-10",
    "reorder_probability": 0.85,
    "reorder_predicted_date": "2024-02-15",
    "churn_risk": "low",
    "segment": "VIP"
  }
}
```

### Quotations

#### GET /quotations

Get list of quotations.

**Query Parameters:**
- `status` (string): Filter by status
- `customer_id` (uuid): Filter by customer
- `date_from` (date): Start date
- `date_to` (date): End date

#### GET /quotations/:id

Get quotation details.

#### POST /quotations

Create new quotation.

**Request Body:**
```json
{
  "customer_id": "customer_uuid",
  "quotation_date": "2024-01-15",
  "valid_until": "2024-02-15",
  "line_items": [
    {
      "product_name": "Custom CNC Part",
      "description": "Precision machined aluminum component",
      "quantity": 100,
      "unit_price": 25.00,
      "estimated_hours": 8.5,
      "material_cost": 500.00
    }
  ],
  "payment_terms": "Net 30",
  "lead_time_days": 14
}
```

#### POST /quotations/:id/calculate-pricing

AI-powered pricing calculation.

**Request Body:**
```json
{
  "line_items": [
    {
      "product_name": "Custom CNC Part",
      "machining_complexity": "medium",
      "material_type": "aluminum",
      "quantity": 100,
      "specifications": {
        "tolerance": "±0.001",
        "surface_finish": "Ra 0.8"
      }
    }
  ],
  "desired_margin_percent": 30.00
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pricing_breakdown": [
      {
        "line_item_index": 0,
        "material_cost": 500.00,
        "machining_time_hours": 8.5,
        "labor_cost": 850.00,
        "overhead": 425.00,
        "total_cost": 1775.00,
        "suggested_price": 25.36,
        "margin_percent": 30.0,
        "confidence_score": 0.88
      }
    ],
    "total_amount": 2536.00
  }
}
```

#### POST /quotations/:id/send

Send quotation to customer.

#### POST /quotations/:id/accept

Mark quotation as accepted.

#### GET /quotations/:id/pdf

Generate and download quotation PDF.

### Sales Opportunities

#### GET /opportunities

Get list of sales opportunities.

**Query Parameters:**
- `stage` (string): Filter by stage
- `assigned_to` (uuid): Filter by assigned user
- `status` (string): 'open', 'won', 'lost'

#### GET /opportunities/:id

Get opportunity details.

#### POST /opportunities

Create new opportunity.

**Request Body:**
```json
{
  "opportunity_name": "XYZ Manufacturing - Q1 Order",
  "customer_id": "customer_uuid",
  "estimated_value": 50000.00,
  "stage": "qualification",
  "expected_close_date": "2024-03-31",
  "source": "website"
}
```

#### PUT /opportunities/:id

Update opportunity.

#### GET /opportunities/:id/win-probability

Get AI-calculated win probability.

**Response:**
```json
{
  "success": true,
  "data": {
    "opportunity_id": "opportunity_uuid",
    "win_probability": 0.75,
    "factors": {
      "customer_relationship": 0.9,
      "product_fit": 0.8,
      "timing": 0.7,
      "competitive_landscape": 0.6
    },
    "recommendations": [
      "Schedule technical demo",
      "Provide case study from similar customer"
    ]
  }
}
```

### Orders

#### GET /orders

Get list of orders.

#### GET /orders/:id

Get order details.

#### POST /orders

Create new order from quotation.

**Request Body:**
```json
{
  "quotation_id": "quotation_uuid",
  "order_date": "2024-01-20",
  "required_date": "2024-02-10"
}
```

---

## Email/Chatbot Module APIs

### Emails

#### GET /emails

Get list of emails.

**Query Parameters:**
- `category` (string): Filter by category
- `status` (string): Filter by status
- `customer_id` (uuid): Filter by customer
- `priority` (string): Filter by priority
- `is_unread` (boolean): Only unread emails

#### GET /emails/:id

Get email details.

#### POST /emails/:id/reply

Send reply to email (automated or manual).

**Request Body:**
```json
{
  "content": "Thank you for your inquiry. We will get back to you shortly.",
  "use_template": false,
  "template_id": null,
  "auto_generate": true
}
```

#### POST /emails/:id/forward

Forward email.

#### PUT /emails/:id/category

Update email category.

#### PUT /emails/:id/priority

Update email priority.

#### POST /emails/:id/mark-read

Mark email as read.

### Conversations (Chatbot)

#### GET /conversations

Get list of conversations.

**Query Parameters:**
- `status` (string): Filter by status
- `channel` (string): Filter by channel
- `customer_id` (uuid): Filter by customer

#### GET /conversations/:id

Get conversation details with messages.

#### POST /conversations/:id/messages

Send a message in conversation.

**Request Body:**
```json
{
  "content": "What is the status of my order?",
  "channel": "web_chat"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "message_uuid",
      "content": "Your order #ORD-2024-001 is currently in production. Expected completion date: 2024-02-10.",
      "direction": "outbound",
      "sender_type": "bot",
      "sent_at": "2024-01-15T10:30:00Z"
    },
    "intent": "order_status",
    "confidence": 0.95
  }
}
```

#### POST /conversations/:id/escalate

Escalate conversation to human agent.

**Request Body:**
```json
{
  "reason": "Customer requested human assistance",
  "assigned_to": "user_uuid"
}
```

### Knowledge Base

#### GET /knowledge-base/articles

Get list of knowledge base articles.

#### GET /knowledge-base/articles/:id

Get article details.

#### POST /knowledge-base/articles

Create new article.

**Request Body:**
```json
{
  "title": "How to Track Your Order",
  "content": "You can track your order status by...",
  "category": "orders",
  "tags": ["tracking", "orders", "shipping"],
  "status": "published"
}
```

#### GET /knowledge-base/search

Search knowledge base.

**Query Parameters:**
- `query` (string): Search query (required)
- `category` (string): Filter by category
- `limit` (integer): Max results

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "article_uuid",
        "title": "How to Track Your Order",
        "summary": "You can track your order status...",
        "relevance_score": 0.92,
        "category": "orders"
      }
    ],
    "total": 5
  }
}
```

---

## Dashboard & Analytics APIs

### Dashboard

#### GET /dashboard/overview

Get dashboard overview data.

**Response:**
```json
{
  "success": true,
  "data": {
    "financial_summary": {
      "revenue_today": 5000.00,
      "revenue_month": 150000.00,
      "outstanding_receivables": 75000.00,
      "outstanding_payables": 45000.00,
      "cash_position": 250000.00
    },
    "sales_summary": {
      "active_opportunities": 25,
      "pipeline_value": 500000.00,
      "orders_today": 3,
      "orders_month": 45
    },
    "operations_summary": {
      "low_stock_items": 5,
      "pending_pos": 12,
      "pending_approvals": 8
    },
    "alerts": [
      {
        "type": "overdue_payment",
        "severity": "high",
        "message": "3 invoices are overdue",
        "count": 3
      }
    ]
  }
}
```

#### GET /dashboard/kpis

Get key performance indicators.

**Query Parameters:**
- `period` (string): 'today', 'week', 'month', 'year'
- `compare_with` (string): Previous period comparison

### Analytics

#### GET /analytics/revenue-trend

Get revenue trend data.

**Query Parameters:**
- `start_date` (date): Required
- `end_date` (date): Required
- `group_by` (string): 'day', 'week', 'month'

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "total_revenue": 150000.00,
    "data_points": [
      {
        "period": "2024-01-01",
        "revenue": 5000.00,
        "orders": 3
      },
      {
        "period": "2024-01-02",
        "revenue": 7500.00,
        "orders": 5
      }
    ],
    "trend": "up",
    "growth_percent": 15.5
  }
}
```

#### GET /analytics/sales-performance

Get sales performance analytics.

#### GET /analytics/customer-analysis

Get customer analytics.

---

## Webhooks

### Webhook Configuration

#### GET /webhooks

Get list of configured webhooks.

#### POST /webhooks

Create new webhook.

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": [
    "invoice.created",
    "invoice.paid",
    "order.completed"
  ],
  "secret": "webhook_secret_key",
  "is_active": true
}
```

#### PUT /webhooks/:id

Update webhook.

#### DELETE /webhooks/:id

Delete webhook.

### Available Webhook Events

**Accounting Events:**
- `invoice.created`
- `invoice.sent`
- `invoice.paid`
- `invoice.overdue`
- `payment.received`
- `document.processed`

**Purchasing Events:**
- `purchase_order.created`
- `purchase_order.approved`
- `delivery.received`
- `material.low_stock`

**Sales Events:**
- `quotation.created`
- `quotation.accepted`
- `order.created`
- `opportunity.won`
- `opportunity.lost`

**Email/Chatbot Events:**
- `email.received`
- `email.sent`
- `conversation.started`
- `conversation.escalated`

### Webhook Payload Format

```json
{
  "event": "invoice.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "invoice_uuid",
    "invoice_number": "INV-2024-001",
    "customer_id": "customer_uuid",
    "total_amount": 15000.00,
    "status": "draft"
  }
}
```

### Webhook Security

Webhooks include an `X-Signature` header with HMAC-SHA256 signature:

```
X-Signature: sha256=abc123def456...
```

Verify signature using the webhook secret.

---

## Rate Limiting

### Rate Limits

- **Standard Tier:** 1,000 requests/hour per API key
- **Professional Tier:** 10,000 requests/hour per API key
- **Enterprise Tier:** 100,000 requests/hour per API key

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642156800
```

### Rate Limit Exceeded Response

**Status Code:** 429 Too Many Requests

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 3600
  }
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Codes

**Authentication Errors:**
- `AUTH_REQUIRED`: Authentication required
- `AUTH_INVALID`: Invalid credentials
- `AUTH_EXPIRED`: Token expired
- `AUTH_INSUFFICIENT_PERMISSIONS`: Insufficient permissions

**Validation Errors:**
- `VALIDATION_ERROR`: General validation error
- `REQUIRED_FIELD_MISSING`: Required field is missing
- `INVALID_FORMAT`: Invalid data format
- `INVALID_VALUE`: Invalid field value

**Resource Errors:**
- `RESOURCE_NOT_FOUND`: Resource not found
- `RESOURCE_ALREADY_EXISTS`: Resource already exists
- `RESOURCE_CONFLICT`: Resource conflict

**Business Logic Errors:**
- `INSUFFICIENT_STOCK`: Insufficient inventory
- `INVALID_TRANSACTION`: Invalid transaction
- `WORKFLOW_ERROR`: Workflow error

### Error Response Example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "fields": [
        {
          "field": "email",
          "message": "Invalid email format"
        },
        {
          "field": "amount",
          "message": "Amount must be greater than 0"
        }
      ]
    },
    "request_id": "req_abc123"
  }
}
```

---

## SDKs and Libraries

### Official SDKs

- **JavaScript/TypeScript:** `npm install @unified-ai-assistant/sdk`
- **Python:** `pip install unified-ai-assistant`
- **PHP:** `composer require unified-ai-assistant/sdk`
- **Ruby:** `gem install unified-ai-assistant`

### Example Usage (JavaScript)

```javascript
import { UnifiedAIAssistant } from '@unified-ai-assistant/sdk';

const client = new UnifiedAIAssistant({
  apiKey: 'your_api_key',
  environment: 'production'
});

// Create invoice
const invoice = await client.invoices.create({
  customer_id: 'customer_uuid',
  invoice_date: '2024-01-15',
  line_items: [
    {
      description: 'CNC Machining Services',
      quantity: 10,
      unit_price: 1500.00
    }
  ]
});

// Get invoices
const invoices = await client.invoices.list({
  status: 'unpaid',
  limit: 50
});
```

---

## API Versioning

The API uses URL-based versioning:

- Current version: `/v1/`
- New versions: `/v2/`, `/v3/`, etc.

Breaking changes will result in a new version. Non-breaking changes (new endpoints, optional parameters) are added to the current version.

---

**Document Control:**
- **Author:** API Development Team
- **Last Review:** 2024
- **API Version:** 1.0



