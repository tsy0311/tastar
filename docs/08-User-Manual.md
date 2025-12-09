# User Manual
## Unified AI Business Assistant for CNC Factory

**Version:** 1.0  
**Last Updated:** 2024  
**Audience:** End Users

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Accounting Module](#accounting-module)
4. [Purchasing Module](#purchasing-module)
5. [Sales Module](#sales-module)
6. [Email & Chatbot Module](#email--chatbot-module)
7. [Reports & Analytics](#reports--analytics)
8. [Settings & Configuration](#settings--configuration)
9. [Troubleshooting](#troubleshooting)
10. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Getting Started

### First Login

1. **Access the Application**
   - Open your web browser
   - Navigate to: `https://app.unified-ai-assistant.com`
   - Enter your email and password
   - Click "Sign In"

2. **Complete Your Profile**
   - Click on your profile icon (top right)
   - Select "My Profile"
   - Fill in your information:
     - Full name
     - Phone number
     - Timezone
     - Language preference
   - Click "Save"

3. **Take the Tour**
   - Click "Take Tour" button on first login
   - Follow the guided tour to learn the interface
   - You can skip or restart the tour anytime

### Navigation Basics

**Main Navigation:**
- **Sidebar:** Left side contains main modules
  - 📊 Dashboard
  - 💰 Accounting
  - 📦 Purchasing
  - 📈 Sales
  - 💬 Communication
  - ⚙️ Settings

**Top Bar:**
- **Search:** Global search for any item
- **Notifications:** Bell icon for alerts
- **Profile:** Your account menu

### Quick Actions

From anywhere in the application, you can:
- Press `Ctrl+K` (or `Cmd+K` on Mac) for command palette
- Use `+` button (top right) for quick create menu
- Use keyboard shortcuts (see section at end)

---

## Dashboard Overview

### What You'll See

The dashboard shows key information at a glance:

**KPI Cards (Top Row):**
- **Revenue Today:** Today's total revenue
- **Outstanding AR:** Money owed to you
- **Outstanding AP:** Money you owe
- **Cash Position:** Current cash balance

**Quick Actions:**
- Create Invoice
- Create Purchase Order
- New Quotation
- Send Email

**Recent Activity:**
- Latest transactions and actions
- Click any item to view details

**Alerts Panel:**
- Overdue payments
- Low stock items
- Pending approvals
- Urgent emails

**Revenue Trend Chart:**
- Visual graph of revenue over time
- Click to see detailed report

### Customizing Your Dashboard

1. Click "Customize Dashboard" (top right)
2. Drag widgets to rearrange
3. Add/remove widgets as needed
4. Click "Save" to apply changes

---

## Accounting Module

### Managing Customers

#### Adding a New Customer

1. Go to **Accounting > Customers**
2. Click **"+ New Customer"** button
3. Fill in the form:
   - **Customer Code:** Unique identifier (e.g., CUST-001)
   - **Name:** Company name
   - **Contact Information:** Email, phone
   - **Billing Address:** Complete address
   - **Credit Limit:** Maximum credit allowed
   - **Payment Terms:** Net 30, Net 60, etc.
4. Click **"Save"**

#### Editing Customer Information

1. Go to **Accounting > Customers**
2. Find the customer in the list
3. Click on the customer name
4. Click **"Edit"** button
5. Make your changes
6. Click **"Save"**

### Creating Invoices

#### Automatic Invoice Generation (Recommended)

1. When a job is completed in your production system:
   - The system automatically creates a draft invoice
   - You'll receive a notification

2. Go to **Accounting > Invoices**
3. Find the draft invoice
4. Review the details
5. Click **"Approve & Send"**
   - Invoice is automatically sent to customer via email

#### Manual Invoice Creation

1. Go to **Accounting > Invoices**
2. Click **"+ New Invoice"** button
3. Select **Customer** (required)
   - Start typing to search
   - Recent customers appear first
4. **Invoice Date:** Automatically set to today (can change)
5. **Due Date:** Automatically calculated based on payment terms
6. **Add Line Items:**
   - Click **"+ Add Line Item"**
   - Enter description
   - Enter quantity
   - Enter unit price
   - System calculates total automatically
   - AI may suggest items based on customer history
7. **Review Totals:**
   - Subtotal
   - Tax (automatically calculated)
   - Total
8. **Add Notes** (optional):
   - Customer-visible notes
   - Internal notes (not visible to customer)
9. Click **"Save Draft"** or **"Save & Send"**

**Pro Tip:** Use AI suggestions (shown in blue) to auto-fill common items!

### Document Processing (OCR)

#### Uploading Documents

1. Go to **Accounting > Documents**
2. Click **"Upload Document"** button
3. Select file(s) or drag and drop
4. Select **Document Type:**
   - Invoice
   - Receipt
   - Purchase Order
   - Delivery Order
5. Click **"Upload"**

#### Reviewing Extracted Data

1. System processes document automatically (30-60 seconds)
2. When complete, you'll see **"Review Required"** status
3. Click on the document to review
4. **Review extracted fields:**
   - Vendor/Supplier name
   - Invoice number
   - Date
   - Amount
   - Line items
5. **Make corrections** if needed:
   - Click on any field to edit
   - System learns from your corrections
6. Click **"Approve"** to create invoice/bill record

### Recording Payments

#### Recording a Payment Received

1. Go to **Accounting > Payments**
2. Click **"+ Record Payment"**
3. Select **Payment Type:** "Receipt"
4. Select **Customer**
5. Enter **Payment Details:**
   - Amount
   - Payment Date
   - Payment Method (Bank Transfer, Check, Cash, etc.)
   - Payment Reference (check number, transaction ID)
6. **Allocate to Invoices:**
   - Select invoices to pay
   - Enter amounts
   - System auto-allocates if only one invoice
7. Click **"Save"**

#### Recording a Payment Made

1. Same process as above
2. Select **Payment Type:** "Payment"
3. Select **Supplier** instead of Customer
4. Allocate to Bills instead of Invoices

### Transaction Matching

#### Three-Way Matching (Automatic)

1. System automatically matches:
   - Purchase Order
   - Delivery Order
   - Invoice/Bill
2. You'll see **"Matched"** status when complete
3. **Review matches:**
   - Go to **Accounting > Matching**
   - Click on any match to see details

#### Handling Exceptions

1. If system finds exceptions:
   - Go to **Accounting > Matching**
   - Find items with **"Exception"** status
2. **Review the exception:**
   - Amount variance
   - Quantity variance
   - Date variance
3. **Resolve:**
   - Accept variance if within tolerance
   - Adjust amounts if needed
   - Mark as resolved

### Financial Reports

#### Viewing Standard Reports

1. Go to **Accounting > Reports**
2. Select report type:
   - **Profit & Loss:** Income and expenses
   - **Balance Sheet:** Assets, liabilities, equity
   - **Accounts Receivable Aging:** Who owes you money
   - **Accounts Payable Aging:** Who you owe money
3. **Set Date Range:**
   - Use presets (This Month, Last Month, This Year)
   - Or select custom dates
4. Click **"Generate Report"**
5. **Export Options:**
   - PDF
   - Excel
   - CSV

#### Creating Custom Reports

1. Go to **Accounting > Reports > Custom Reports**
2. Click **"+ New Report"**
3. **Drag and drop fields** to build your report
4. **Add filters** (date range, customer, status, etc.)
5. **Add calculations** if needed
6. **Preview** your report
7. Click **"Save"** or **"Save & Generate"**

---

## Purchasing Module

### Managing Suppliers

#### Adding a New Supplier

1. Go to **Purchasing > Suppliers**
2. Click **"+ New Supplier"** button
3. Fill in supplier information:
   - **Supplier Code:** Unique identifier
   - **Company Name**
   - **Contact Information**
   - **Address**
   - **Payment Terms**
   - **Default Currency**
4. Click **"Save"**

#### Viewing Supplier Performance

1. Go to **Purchasing > Suppliers**
2. Click on a supplier name
3. View **Performance Metrics:**
   - On-Time Delivery Rate
   - Quality Score
   - Average Rating
   - Total Orders
   - Total Spent

### Managing Materials

#### Adding a New Material

1. Go to **Purchasing > Materials**
2. Click **"+ New Material"** button
3. Fill in material details:
   - **Material Code:** (e.g., MAT-001)
   - **Material Name**
   - **Category**
   - **Unit of Measure:** kg, pieces, meters, etc.
   - **Reorder Point:** Minimum stock level
   - **Reorder Quantity:** How much to order
   - **Safety Stock:** Extra stock buffer
   - **Standard Cost**
4. Click **"Save"**

#### Viewing Inventory Levels

1. Go to **Purchasing > Materials**
2. **Stock Status Indicators:**
   - 🟢 Green: In stock (above reorder point)
   - 🟡 Yellow: Low stock (below reorder point)
   - 🔴 Red: Critical (below safety stock)
3. Click on material to see:
   - Current stock level
   - Recent transactions
   - Forecasted demand

### Creating Purchase Orders

#### Automatic PO Generation (Recommended)

1. **System monitors stock levels:**
   - When stock falls below reorder point
   - System automatically creates draft PO
   - You'll receive notification

2. Go to **Purchasing > Purchase Orders**
3. Find draft POs (marked "Draft")
4. **Review PO:**
   - Check quantities
   - Verify supplier
   - Review pricing
5. Click **"Approve"** or **"Approve & Send"**

#### Manual PO Creation

1. Go to **Purchasing > Purchase Orders**
2. Click **"+ New Purchase Order"**
3. Select **Supplier**
4. Select **Materials:**
   - Click **"+ Add Material"**
   - Search for material
   - Enter quantity
   - System suggests quantity based on forecast
5. **Review Totals**
6. **Set Delivery Date**
7. Click **"Save Draft"** or **"Approve & Send"**

### Demand Forecasting

#### Viewing Forecasts

1. Go to **Purchasing > Forecasts**
2. Select **Material**
3. View **Forecast Chart:**
   - Predicted demand over time
   - Confidence intervals
   - Historical actuals for comparison

#### Understanding Forecasts

- **Forecasted Quantity:** Expected usage
- **Confidence Score:** How reliable (0-100%)
- **Confidence Interval:** Range of likely values
- **Model Type:** Algorithm used (LSTM, ARIMA, etc.)

**Pro Tip:** Forecasts improve over time as system learns your patterns!

### Receiving Deliveries

#### Recording Goods Receipt

1. When delivery arrives:
   - Go to **Purchasing > Deliveries**
   - Find the delivery (or create new)

2. **Record Received Quantities:**
   - Enter quantities received
   - Enter quantities accepted (passed QC)
   - Enter quantities rejected (if any)

3. **Quality Check:**
   - Mark quality status
   - Add inspection notes if needed

4. Click **"Complete Receipt"**
   - Inventory automatically updated
   - PO status updated

---

## Sales Module

### Managing Customers

*Note: Customer management is shared with Accounting module. See Accounting section above.*

### Creating Quotations

#### Using AI Pricing Assistant

1. Go to **Sales > Quotations**
2. Click **"+ New Quotation"**
3. Select **Customer**
4. **Add Line Items:**
   - Click **"+ Add Line Item"**
   - Enter product description
   - Enter quantity

5. **AI Pricing Assistant automatically calculates:**
   - Material cost
   - Machining time (estimated)
   - Labor cost
   - Overhead
   - Suggested price with margin
   - **Confidence Score:** How reliable the estimate

6. **Review AI Suggestions:**
   - Transparent cost breakdown
   - Adjust margin if needed
   - Accept or modify suggested price

7. Click **"Apply AI Suggestion"** or enter price manually

8. **Set Validity Period:**
   - Valid Until date
   - Usually 30 days

9. Click **"Save Draft"** or **"Save & Send"**

#### Manual Quotation Creation

1. Same process as above
2. Skip AI suggestions
3. Enter prices manually
4. System still calculates totals automatically

### Sales Opportunities (Pipeline)

#### Creating an Opportunity

1. Go to **Sales > Opportunities**
2. Click **"+ New Opportunity"**
3. Fill in details:
   - **Opportunity Name**
   - **Customer**
   - **Estimated Value**
   - **Stage:** Qualification, Proposal, Negotiation, Close
   - **Expected Close Date**

4. Click **"Save"**

#### Managing Pipeline

1. **Kanban View** (default):
   - Drag opportunities between stages
   - See value at each stage
   - Quick win probability view

2. **List View:**
   - Sortable table
   - Filter by stage, customer, date
   - Export to Excel

3. **Win Probability:**
   - AI calculates probability (shown as percentage)
   - Based on customer history, stage, value, etc.
   - Updates as opportunity progresses

#### Converting to Order

1. When opportunity is won:
   - Click on opportunity
   - Click **"Mark as Won"**
   - System prompts to create order
   - Click **"Create Order"**

---

## Email & Chatbot Module

### Email Management

#### Accessing Your Inbox

1. Go to **Communication > Inbox**
2. **Email List Shows:**
   - From (sender)
   - Subject
   - Priority (color-coded)
   - Category (auto-categorized)
   - Date received

#### Email Categories

Emails are automatically categorized:
- 📋 **Inquiry:** General questions
- 📦 **Order:** Order-related
- 😠 **Complaint:** Customer issues
- 💰 **Invoice:** Invoice-related
- 📊 **Quotation:** Quote requests

#### Reading Emails

1. Click on email in list
2. **View Email Details:**
   - Full message
   - Attachments (if any)
   - AI-extracted information (if applicable)

#### Replying to Emails

1. Click on email
2. Click **"Reply"** button
3. **AI Suggests Reply:**
   - System analyzes email
   - Generates suggested response
   - **Review and edit** as needed
4. Click **"Send"** or **"Send & Use AI"** (learns from your edits)

#### Sending New Emails

1. Click **"Compose"** button (top right)
2. Enter recipient
3. Enter subject
4. Type message (or use template)
5. **AI Can Help:**
   - Click **"AI Assist"** for suggestions
   - Improve grammar and tone
6. Click **"Send"**

### Email Templates

#### Using Templates

1. When composing email:
   - Click **"Use Template"**
   - Select template
   - Fill in placeholders (marked with {{ }})
   - Customize as needed
   - Send

#### Creating Templates

1. Go to **Communication > Templates**
2. Click **"+ New Template"**
3. Enter template details:
   - **Name**
   - **Subject**
   - **Body:** Use {{customer_name}}, {{order_number}}, etc. for placeholders
4. Click **"Save"**

### Chatbot Configuration

#### Viewing Conversations

1. Go to **Communication > Conversations**
2. See all chatbot conversations
3. Filter by:
   - Status (Active, Resolved, Escalated)
   - Channel (Web Chat, Email, SMS)
   - Customer

#### Responding to Chatbot Escalations

1. When chatbot escalates to human:
   - You'll receive notification
   - Go to **Communication > Conversations**
   - Find escalated conversation
   - Click to continue conversation
   - Customer sees seamless handoff

#### Chatbot Settings

1. Go to **Communication > Chatbot > Settings**
2. **Configure:**
   - Business hours
   - Auto-responses
   - Escalation rules
   - Personality/tone

### Knowledge Base

#### Searching Knowledge Base

1. Click search icon in chatbot
2. Type your question
3. System searches knowledge base
4. Shows relevant articles
5. Customer can read or chatbot can summarize

#### Adding Articles

1. Go to **Communication > Knowledge Base**
2. Click **"+ New Article"**
3. Enter:
   - **Title**
   - **Category**
   - **Content**
   - **Tags** (for search)
4. Click **"Publish"**

---

## Reports & Analytics

### Dashboard Reports

#### Customizing Dashboard

1. Go to **Dashboard**
2. Click **"Customize"** (top right)
3. **Add Widgets:**
   - Revenue trends
   - Top customers
   - Expense breakdown
   - Inventory levels
   - etc.
4. **Rearrange:** Drag widgets
5. **Remove:** Click X on widget
6. Click **"Save"**

### Standard Reports

#### Financial Reports

- **Profit & Loss:** Revenue vs expenses
- **Balance Sheet:** Assets, liabilities, equity
- **Cash Flow:** Cash in and out
- **AR Aging:** Who owes you, how long
- **AP Aging:** Who you owe, how long

#### Sales Reports

- **Sales by Customer:** Top customers
- **Sales by Product:** Best sellers
- **Sales Forecast:** Predicted sales
- **Opportunity Pipeline:** Potential revenue

#### Purchasing Reports

- **Supplier Performance:** Delivery, quality scores
- **Inventory Report:** Stock levels, values
- **Purchase History:** Spending trends
- **Demand Forecast:** Future needs

### Exporting Reports

1. After generating any report:
2. Click **"Export"** button
3. Choose format:
   - **PDF:** For printing/sharing
   - **Excel:** For analysis
   - **CSV:** For data import
4. File downloads automatically

---

## Settings & Configuration

### Company Settings

#### Basic Information

1. Go to **Settings > Company**
2. Update:
   - Company name
   - Logo
   - Address
   - Tax ID
   - Fiscal year start
   - Currency
   - Timezone

#### Financial Settings

1. Go to **Settings > Accounting**
2. Configure:
   - Chart of Accounts
   - Tax rates
   - Payment terms
   - Invoice numbering
   - Default currencies

### User Preferences

#### Personal Settings

1. Click your profile icon (top right)
2. Select **"My Preferences"**
3. Configure:
   - **Language:** UI language
   - **Timezone:** For date/time display
   - **Notifications:** Email, in-app, SMS
   - **Dashboard:** Default view
   - **Theme:** Light/Dark mode

#### Notification Settings

1. Go to **Settings > Notifications**
2. **Configure Alerts:**
   - Email notifications
   - In-app notifications
   - SMS notifications
   - What triggers each notification

### Automation Settings

#### Invoice Automation

1. Go to **Settings > Automation > Invoices**
2. **Configure:**
   - Auto-generate on job completion: ON/OFF
   - Auto-send to customer: ON/OFF
   - Approval required: ON/OFF
   - Email template to use

#### PO Automation

1. Go to **Settings > Automation > Purchase Orders**
2. **Configure:**
   - Auto-generate when stock low: ON/OFF
   - Auto-approve if under amount: $XXX
   - Auto-send to supplier: ON/OFF

#### Email Automation

1. Go to **Settings > Automation > Email**
2. **Configure:**
   - Auto-respond to common queries: ON/OFF
   - Auto-categorize emails: ON/OFF
   - Escalation rules

---

## Troubleshooting

### Common Issues

#### Can't Log In

1. **Check email/password:**
   - Ensure correct email
   - Try password reset

2. **Account locked:**
   - Too many failed attempts
   - Wait 15 minutes or contact admin

3. **Browser issues:**
   - Clear cache and cookies
   - Try different browser
   - Ensure JavaScript enabled

#### Documents Not Processing

1. **Check file format:**
   - Supported: PDF, JPG, PNG, TIFF
   - File size: Max 10MB

2. **OCR Processing:**
   - May take 30-60 seconds
   - Check document quality (clear, readable)
   - If fails, manually enter data

#### Email Not Sending

1. **Check email account settings:**
   - Go to Settings > Email Accounts
   - Verify connection status
   - Test connection

2. **Check recipient email:**
   - Ensure valid email address
   - Check spam/junk folder

#### Slow Performance

1. **Check internet connection**
2. **Clear browser cache**
3. **Reduce date range** in reports
4. **Contact support** if persistent

### Getting Help

#### In-App Help

1. Click **"Help"** icon (question mark)
2. Search knowledge base
3. Browse help articles
4. Contact support

#### Support Options

- **Email:** support@unified-ai-assistant.com
- **Phone:** 1-800-XXX-XXXX
- **Live Chat:** Available in app
- **Knowledge Base:** help.unified-ai-assistant.com

---

## Keyboard Shortcuts

### Global Shortcuts

- `Ctrl+K` / `Cmd+K`: Command palette (search anything)
- `Ctrl+/` / `Cmd+/`: Show all shortcuts
- `Esc`: Close modal/dialog

### Navigation

- `Ctrl+1` / `Cmd+1`: Dashboard
- `Ctrl+2` / `Cmd+2`: Accounting
- `Ctrl+3` / `Cmd+3`: Purchasing
- `Ctrl+4` / `Cmd+4`: Sales
- `Ctrl+5` / `Cmd+5`: Communication
- `Ctrl+,` / `Cmd+,`: Settings

### Common Actions

- `Ctrl+N` / `Cmd+N`: New (context-aware)
  - In Invoices: New Invoice
  - In POs: New PO
  - etc.
- `Ctrl+S` / `Cmd+S`: Save
- `Ctrl+P` / `Cmd+P`: Print
- `Ctrl+F` / `Cmd+F`: Find/Search

### In Lists/Tables

- `Arrow Keys`: Navigate rows
- `Enter`: Open selected item
- `Delete`: Delete selected item
- `/`: Focus search box

---

## Tips & Best Practices

### Efficiency Tips

1. **Use AI Suggestions:**
   - AI learns from your usage
   - Accept suggestions to save time
   - System gets smarter over time

2. **Keyboard Shortcuts:**
   - Learn common shortcuts
   - Much faster than clicking

3. **Bulk Actions:**
   - Select multiple items
   - Perform action on all at once

4. **Templates:**
   - Create templates for common tasks
   - Reuse instead of starting from scratch

5. **Automation:**
   - Enable automation where possible
   - Set up approval workflows
   - Let system handle routine tasks

### Data Quality

1. **Complete Customer/Supplier Profiles:**
   - More data = better AI predictions
   - Accurate addresses for invoicing

2. **Regular Reviews:**
   - Review AI suggestions
   - Correct errors promptly
   - System learns from corrections

3. **Consistent Naming:**
   - Use consistent material codes
   - Standard naming conventions
   - Easier searching and reporting

### Security

1. **Strong Passwords:**
   - Use unique, strong passwords
   - Enable two-factor authentication

2. **Logout When Done:**
   - Especially on shared computers

3. **Review Permissions:**
   - Only grant necessary access
   - Regular access audits

---

## Appendix

### Supported File Formats

**Documents:**
- PDF (.pdf)
- Images: JPG, PNG, TIFF

**Exports:**
- PDF
- Excel (.xlsx)
- CSV (.csv)

### Browser Requirements

**Recommended:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Minimum:**
- JavaScript enabled
- Cookies enabled
- Modern browser (last 2 versions)

### Mobile App

**Available For:**
- iOS 14+ (App Store)
- Android 10+ (Play Store)

**Features:**
- All core features
- Push notifications
- Offline mode (limited)
- Touch-optimized interface

---

**Need More Help?**

- **Knowledge Base:** help.unified-ai-assistant.com
- **Video Tutorials:** youtube.com/unified-ai-assistant
- **Support:** support@unified-ai-assistant.com
- **Phone:** 1-800-XXX-XXXX

---

**Last Updated:** 2024  
**Version:** 1.0




