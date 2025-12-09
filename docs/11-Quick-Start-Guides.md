# Quick Start Guides
## Unified AI Business Assistant for CNC Factory

**Version:** 1.0  
**Last Updated:** 2024

---

## Overview

These quick start guides help different user roles get up and running quickly with the Unified AI Business Assistant. Each guide is tailored to specific needs and workflows.

---

## Table of Contents

1. [For System Administrators](#for-system-administrators)
2. [For Developers](#for-developers)
3. [For Accountants](#for-accountants)
4. [For Purchasing Managers](#for-purchasing-managers)
5. [For Sales Teams](#for-sales-teams)
6. [For End Users](#for-end-users)

---

## For System Administrators

### Initial Setup (30 minutes)

#### 1. Access the System
- Navigate to: `https://app.unified-ai-assistant.com`
- Login with admin credentials
- Complete initial setup wizard

#### 2. Configure Company Settings
- **Company Information:**
  - Company name, address, tax ID
  - Logo upload
  - Timezone and locale
  - Currency settings

- **Financial Settings:**
  - Fiscal year start date
  - Chart of accounts setup
  - Tax rates configuration
  - Payment terms defaults

#### 3. Set Up Users
```bash
# Create user accounts
1. Go to Settings > Users
2. Click "Add User"
3. Fill in user details
4. Assign roles (Admin, Accountant, Purchasing, Sales, Viewer)
5. Send invitation email
```

#### 4. Configure Integrations
- **Email Integration:**
  - Connect email accounts (Gmail, Outlook, IMAP)
  - Configure email routing rules
  - Set up auto-response templates

- **Third-Party Services:**
  - OCR service (Google Cloud Vision, AWS Textract)
  - AI service (OpenAI, Claude)
  - Payment gateway (if needed)

#### 5. Set Up Workflows
- Configure approval workflows
- Set up notification preferences
- Configure automated rules

### Daily Tasks Checklist

- [ ] Review system alerts and notifications
- [ ] Check system health dashboard
- [ ] Review pending approvals
- [ ] Monitor user activity logs
- [ ] Check backup status

### Key Resources
- [Deployment Guide](./09-Deployment-Guide.md) - For infrastructure setup
- [User Manual](./08-User-Manual.md) - For user management
- [System Design Document](./01-System-Design-Document.md) - For architecture understanding

---

## For Developers

### Development Environment Setup (1 hour)

#### 1. Prerequisites
```bash
# Required tools
- Node.js 18+ or Python 3.10+
- Docker and Docker Compose
- Git
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)
```

#### 2. Clone Repository
```bash
git clone https://github.com/tsy0311/tastar.git
cd tastar
```

#### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install  # or pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start database and Redis
docker-compose up -d postgres redis

# Run migrations
npm run migrate  # or python manage.py migrate

# Start development server
npm run dev  # or python manage.py runserver
```

#### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with API URL

# Start development server
npm run dev
```

#### 5. Access Application
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### First API Call

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "password": "password"
  }'

# Use token for API calls
curl -X GET http://localhost:8000/api/v1/invoices \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Key Resources
- [API Specification](./04-API-Specification.md) - Complete API documentation
- [Database Schema](./03-Database-Schema.md) - Database structure
- [System Design Document](./01-System-Design-Document.md) - Architecture details
- [Development Phases](./06-Development-Phases.md) - Project roadmap

---

## For Accountants

### Getting Started (15 minutes)

#### 1. First Login
- Access: `https://app.unified-ai-assistant.com`
- Login with your credentials
- Complete profile setup

#### 2. Key Features to Explore

**Invoice Management:**
1. Go to **Accounting > Invoices**
2. Click **"Create Invoice"**
3. Select customer
4. Add line items
5. Review and send

**Payment Recording:**
1. Go to **Accounting > Payments**
2. Click **"Record Payment"**
3. Select customer
4. Enter payment details
5. Allocate to invoices

**Document Processing:**
1. Go to **Accounting > Documents**
2. Click **"Upload Document"**
3. Drag and drop invoice/receipt
4. Review extracted data
5. Approve or edit

#### 3. Daily Workflow

**Morning (15 minutes):**
- Review dashboard for alerts
- Check overdue invoices
- Process new documents

**Throughout Day:**
- Record payments as received
- Review and approve invoices
- Match transactions (PO, DO, Invoice)

**End of Day (10 minutes):**
- Review pending items
- Check payment allocations
- Generate daily reports

### Common Tasks

**Create Invoice:**
```
Accounting > Invoices > Create Invoice
- Select customer
- Add line items
- Set due date
- Send to customer
```

**Record Payment:**
```
Accounting > Payments > Record Payment
- Select customer
- Enter amount
- Allocate to invoices
- Save
```

**Three-Way Matching:**
```
Accounting > Matching > Pending Matches
- Review suggested matches
- Approve or flag exceptions
- Resolve discrepancies
```

### Key Resources
- [User Manual - Accounting Module](./08-User-Manual.md#accounting-module) - Detailed guide
- [Feature List - Accounting](./02-Feature-List.md#1-ai-accounting-module-features) - All features

---

## For Purchasing Managers

### Getting Started (15 minutes)

#### 1. Initial Setup
- Login to the system
- Review supplier database
- Set up material master data
- Configure reorder points

#### 2. Key Features to Explore

**Material Management:**
1. Go to **Purchasing > Materials**
2. Review current stock levels
3. Check low stock alerts
4. Update material information

**Purchase Order Creation:**
1. Go to **Purchasing > Purchase Orders**
2. Click **"Create PO"**
3. Select supplier
4. Add materials and quantities
5. Submit for approval

**Demand Forecasting:**
1. Go to **Purchasing > Forecasts**
2. Review AI-generated forecasts
3. Adjust if needed
4. Use for PO planning

#### 3. Daily Workflow

**Morning (20 minutes):**
- Review low stock alerts
- Check pending POs
- Review delivery status

**Throughout Day:**
- Create POs for low stock items
- Review supplier quotes
- Track deliveries

**End of Day (10 minutes):**
- Review forecast accuracy
- Update supplier information
- Plan next day's orders

### Common Tasks

**Create Purchase Order:**
```
Purchasing > Purchase Orders > Create PO
- Select supplier
- Add materials
- Set delivery date
- Submit for approval
```

**Check Inventory:**
```
Purchasing > Materials
- View current stock
- Check reorder points
- Review stock history
```

**Track Delivery:**
```
Purchasing > Deliveries
- View delivery status
- Record goods receipt
- Update quality status
```

### Key Resources
- [User Manual - Purchasing Module](./08-User-Manual.md#purchasing-module) - Detailed guide
- [Feature List - Purchasing](./02-Feature-List.md#2-ai-purchasing-module-features) - All features

---

## For Sales Teams

### Getting Started (15 minutes)

#### 1. Initial Setup
- Login to the system
- Review customer database
- Set up quotation templates
- Configure pricing rules

#### 2. Key Features to Explore

**Quotation Creation:**
1. Go to **Sales > Quotations**
2. Click **"Create Quotation"**
3. Select customer
4. Use AI pricing calculator
5. Send to customer

**Opportunity Management:**
1. Go to **Sales > Opportunities**
2. Create new opportunity
3. Track through pipeline
4. Update win probability

**Customer Intelligence:**
1. Go to **Sales > Customers**
2. Select customer
3. View intelligence dashboard
4. Check reorder predictions

#### 3. Daily Workflow

**Morning (15 minutes):**
- Review new inquiries
- Check opportunity pipeline
- Review customer alerts

**Throughout Day:**
- Create quotations
- Follow up on opportunities
- Respond to customer emails

**End of Day (10 minutes):**
- Update opportunity status
- Review quotation conversion
- Plan follow-ups

### Common Tasks

**Create Quotation:**
```
Sales > Quotations > Create Quotation
- Select customer
- Add products/services
- Use AI pricing
- Send to customer
```

**Track Opportunity:**
```
Sales > Opportunities
- Create opportunity
- Move through stages
- Update win probability
- Close won/lost
```

**Customer Intelligence:**
```
Sales > Customers > [Select Customer]
- View purchase history
- Check reorder prediction
- Review lifetime value
```

### Key Resources
- [User Manual - Sales Module](./08-User-Manual.md#sales-module) - Detailed guide
- [Feature List - Sales](./02-Feature-List.md#3-ai-sales-assistant-module-features) - All features

---

## For End Users

### Getting Started (10 minutes)

#### 1. First Login
- Access: `https://app.unified-ai-assistant.com`
- Login with your credentials
- Complete profile setup

#### 2. Dashboard Overview
- **Key Metrics:** Revenue, AR, AP, Cash
- **Quick Actions:** Create invoice, PO, quotation
- **Alerts:** Overdue payments, low stock
- **Recent Activity:** Latest transactions

#### 3. Navigation Basics
- **Sidebar:** Main modules (Dashboard, Accounting, Purchasing, Sales, Communication)
- **Search:** Global search (Ctrl+K or Cmd+K)
- **Notifications:** Bell icon for alerts
- **Profile:** User menu and settings

#### 4. Common Tasks

**View Dashboard:**
- Automatically shown on login
- Shows key metrics and alerts
- Quick access to common actions

**Search Anything:**
- Press `Ctrl+K` (or `Cmd+K` on Mac)
- Type to search for invoices, customers, materials, etc.
- Select result to navigate

**Create New Item:**
- Click `+` button (top right)
- Select item type (Invoice, PO, Quotation, etc.)
- Fill in form and save

**View Reports:**
- Go to **Reports** section
- Select report type
- Set date range
- Generate and export

### Keyboard Shortcuts

- `Ctrl+K` / `Cmd+K`: Global search
- `Ctrl+/` / `Cmd+/`: Show shortcuts
- `Ctrl+N` / `Cmd+N`: Create new item
- `Esc`: Close modal/dialog
- `?`: Help menu

### Getting Help

- **In-App Help:** Click `?` icon for context-sensitive help
- **User Manual:** [Full User Manual](./08-User-Manual.md)
- **Support:** Click "Support" in user menu
- **Tutorials:** Access from Help menu

### Key Resources
- [User Manual](./08-User-Manual.md) - Complete user guide
- [Glossary](./00-Glossary.md) - Term definitions
- [Feature List](./02-Feature-List.md) - All available features

---

## Tips for All Users

### Best Practices

1. **Use Search:** The global search is powerful - use it instead of navigating
2. **Set Up Notifications:** Configure email/SMS notifications for important events
3. **Use Keyboard Shortcuts:** Learn shortcuts to work faster
4. **Review Dashboard Daily:** Check alerts and metrics every morning
5. **Keep Data Updated:** Regularly update customer, supplier, and material information

### Getting Support

- **Documentation:** Check relevant documentation first
- **In-App Help:** Use the `?` icon for context-sensitive help
- **Support Email:** support@unified-ai-assistant.com
- **Knowledge Base:** Available in the application

---

**Related Documents:**
- [User Manual](./08-User-Manual.md) - Comprehensive user guide
- [Glossary](./00-Glossary.md) - Term definitions
- [Feature List](./02-Feature-List.md) - All features
- [API Specification](./04-API-Specification.md) - For developers

---

**Document Control:**
- **Author:** Documentation Team
- **Last Review:** 2024
- **Version:** 1.0


