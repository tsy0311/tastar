# Manual Implementation Guide

This guide covers all the manual steps required to set up and configure the newly implemented improvements.

## 📋 Table of Contents

1. [Environment Configuration](#1-environment-configuration)
2. [Dependencies Installation](#2-dependencies-installation)
3. [Database Setup](#3-database-setup)
4. [Redis Configuration](#4-redis-configuration)
5. [Integration Setup](#5-integration-setup)
6. [ML Model Training](#6-ml-model-training)
7. [Testing & Validation](#7-testing--validation)
8. [Frontend Integration](#8-frontend-integration)
9. [Production Deployment](#9-production-deployment)

---

## 1. Environment Configuration

### Step 1.1: Create `.env` File

Create or update `backend/.env` with the following variables:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/unified_ai
REDIS_URL=redis://localhost:6379

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# AI Services (Optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Email Service (Choose one)
SENDGRID_API_KEY=your-sendgrid-key
# OR use SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Integration Settings (Configure as needed)
ERP_TYPE=sap  # or oracle, netsuite, etc.
ERP_API_KEY=your-erp-api-key
ERP_BASE_URL=https://api.erp.example.com

ACCOUNTING_TYPE=quickbooks  # or xero, sage, etc.
ACCOUNTING_API_KEY=your-accounting-api-key
ACCOUNTING_BASE_URL=https://api.accounting.example.com

# Multi-Tenant (Optional)
MULTI_TENANT_ENABLED=False
TENANT_ISOLATION_STRICT=True

# File Storage (Optional - for S3)
STORAGE_TYPE=local  # or s3
AWS_S3_BUCKET=your-bucket-name
AWS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Step 1.2: Verify Configuration

```bash
cd backend
python scripts/validate_env.py
```

---

## 2. Dependencies Installation

### Step 2.1: Install Python Dependencies

All required packages are already in `requirements.txt`. Verify installation:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Note:** If you encounter issues with `scikit-learn` or `torch`, you may need to:
- Install system dependencies (see below)
- Use pre-built wheels: `pip install scikit-learn --only-binary :all:`

### Step 2.2: System Dependencies (macOS/Linux)

For ML libraries, you may need:

```bash
# macOS
brew install openblas
brew install libomp

# Ubuntu/Debian
sudo apt-get install build-essential
sudo apt-get install libopenblas-dev
sudo apt-get install libomp-dev
```

### Step 2.3: Verify Installation

```bash
python -c "import sklearn; import torch; import transformers; print('All ML dependencies installed')"
```

---

## 3. Database Setup

### Step 3.1: Create Database

```bash
# Using PostgreSQL CLI
createdb unified_ai

# Or using psql
psql -U postgres
CREATE DATABASE unified_ai;
\q
```

### Step 3.2: Run Migrations

```bash
cd backend
alembic upgrade head
```

### Step 3.3: Verify Database Connection

```bash
python scripts/check_health.py
```

### Step 3.4: Create Database Indexes (Optional but Recommended)

The query optimizer can create indexes automatically, but you can also create them manually:

```sql
-- Example indexes for performance
CREATE INDEX idx_invoices_company_date ON invoices(company_id, invoice_date);
CREATE INDEX idx_customers_company_name ON customers(company_id, name);
CREATE INDEX idx_bills_company_status ON bills(company_id, status);
```

---

## 4. Redis Configuration

### Step 4.1: Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Docker
docker run -d -p 6379:6379 redis:latest
```

### Step 4.2: Verify Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Step 4.3: Configure Redis (Optional)

Edit `/etc/redis/redis.conf` or create `backend/redis.conf`:

```conf
# Memory settings
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence (optional)
save 900 1
save 300 10
```

---

## 5. Integration Setup

### Step 5.1: ERP Integration

**For SAP:**
1. Obtain SAP API credentials from your SAP administrator
2. Get API endpoint URL
3. Configure via API or environment variables:

```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/integrations/erp/configure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "erp_type": "sap",
    "api_key": "your-sap-api-key",
    "base_url": "https://api.sap.com/v1"
  }'
```

**For Other ERP Systems:**
- Oracle: Similar process, get Oracle Cloud credentials
- NetSuite: Use NetSuite REST API credentials
- Custom: Update `integration_service.py` with your ERP's API format

### Step 5.2: Accounting Software Integration

**For QuickBooks:**
1. Create QuickBooks app at https://developer.intuit.com/
2. Get OAuth credentials
3. Configure:

```bash
curl -X POST "http://localhost:8000/api/v1/integrations/accounting/configure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "accounting_type": "quickbooks",
    "api_key": "your-quickbooks-key",
    "base_url": "https://sandbox-quickbooks.api.intuit.com"
  }'
```

**For Xero:**
1. Register app at https://developer.xero.com/
2. Get OAuth credentials
3. Configure similarly

### Step 5.3: Email Service Integration

**Option A: SendGrid**
1. Sign up at https://sendgrid.com/
2. Create API key
3. Configure:

```bash
# Via environment variable (recommended)
SENDGRID_API_KEY=your-sendgrid-api-key

# Or via API
curl -X POST "http://localhost:8000/api/v1/integrations/email/configure" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "email_type": "sendgrid",
    "api_key": "your-sendgrid-api-key"
  }'
```

**Option B: SMTP**
1. Get SMTP credentials from your email provider
2. Configure in `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**For Gmail:** You'll need an "App Password" (not your regular password):
1. Enable 2FA on Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"

### Step 5.4: Test Integrations

```bash
# Check integration status
curl -X GET "http://localhost:8000/api/v1/integrations/status" \
  -H "Authorization: Bearer <your-token>"

# Test email
curl -X POST "http://localhost:8000/api/v1/integrations/email/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

---

## 6. ML Model Training

### Step 6.1: Download Datasets

```bash
cd backend
python ml/scripts/download_datasets.py --type all
```

This downloads:
- Document classification data
- Sentiment analysis data
- Entity extraction data
- Invoice extraction data
- Demand forecasting data

### Step 6.2: Modify Datasets (Optional)

```bash
python ml/scripts/modify_datasets.py --type all
```

This improves dataset quality with:
- Text cleaning
- Feature engineering
- Label normalization
- Duplicate removal

### Step 6.3: Train Base Models

```bash
# Train all models
python ml/scripts/train_all_models.py

# Or train individually
python ml/scripts/train_document_classifier.py --data ml/data/processed/documents_combined.csv
python ml/scripts/train_sentiment_analyzer.py --data ml/data/processed/sentiment_combined.csv
```

### Step 6.4: Hyperparameter Tuning (Optional but Recommended)

```bash
# Tune document classifier
python ml/scripts/hyperparameter_tuning.py \
  --model document \
  --method random \
  --n-iter 50 \
  --data ml/data/processed/documents_combined.csv

# Tune sentiment analyzer
python ml/scripts/hyperparameter_tuning.py \
  --model sentiment \
  --method grid \
  --data ml/data/processed/sentiment_combined.csv
```

**Note:** This can take 30-60 minutes depending on dataset size and iterations.

### Step 6.5: Train Transformer Models (Optional)

**Prerequisites:**
- GPU recommended (but not required)
- 8GB+ RAM recommended
- Can take 1-3 hours per model

```bash
# Train document classifier with DistilBERT
python ml/scripts/train_transformer_models.py \
  --model document \
  --base-model distilbert-base-uncased \
  --epochs 3 \
  --batch-size 16 \
  --data ml/data/processed/documents_combined.csv

# Train sentiment analyzer
python ml/scripts/train_transformer_models.py \
  --model sentiment \
  --base-model distilbert-base-uncased \
  --epochs 3
```

### Step 6.6: Generate Visualizations

```bash
python ml/scripts/generate_visualizations.py
```

This creates:
- Confusion matrices
- Feature importance plots
- Forecast visualizations
- Entity extraction demos

---

## 7. Testing & Validation

### Step 7.1: Start Backend Server

```bash
cd backend
python run.py
```

Server should start on `http://localhost:8000`

### Step 7.2: Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analytics Endpoints:**
```bash
# Get dashboard summary
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard-summary" \
  -H "Authorization: Bearer <your-token>"

# Get revenue trends
curl -X GET "http://localhost:8000/api/v1/analytics/revenue-trends?start_date=2024-01-01&end_date=2024-12-31&granularity=month" \
  -H "Authorization: Bearer <your-token>"
```

**Integration Endpoints:**
```bash
# Check integration status
curl -X GET "http://localhost:8000/api/v1/integrations/status" \
  -H "Authorization: Bearer <your-token>"
```

### Step 7.3: Test Caching

```bash
# First request (cache miss)
time curl -X GET "http://localhost:8000/api/v1/analytics/dashboard-summary" \
  -H "Authorization: Bearer <your-token>"

# Second request (cache hit - should be faster)
time curl -X GET "http://localhost:8000/api/v1/analytics/dashboard-summary" \
  -H "Authorization: Bearer <your-token>"
```

### Step 7.4: Test ML Models

```python
# Test document classifier
from app.services.ml_service import MLService

ml_service = MLService()
result = ml_service.classify_document("Invoice #12345 dated 2024-01-15")
print(result)

# Test sentiment analyzer
result = ml_service.analyze_sentiment("This is a great product!")
print(result)
```

### Step 7.5: Verify Database Queries

Check logs for query performance:
```bash
tail -f backend/logs/combined.log | grep "query"
```

---

## 8. Frontend Integration

### Step 8.1: Update Frontend API Calls

Add new endpoints to your frontend API client:

```javascript
// analytics.js
export const getDashboardSummary = async (token) => {
  const response = await fetch('http://localhost:8000/api/v1/analytics/dashboard-summary', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

export const getRevenueTrends = async (token, startDate, endDate, granularity) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/analytics/revenue-trends?start_date=${startDate}&end_date=${endDate}&granularity=${granularity}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
};
```

### Step 8.2: Create Analytics Dashboard Component

```javascript
// Dashboard.jsx
import { useEffect, useState } from 'react';
import { getDashboardSummary, getRevenueTrends } from './api/analytics';

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      const token = localStorage.getItem('token');
      const summaryData = await getDashboardSummary(token);
      setSummary(summaryData);
      
      const trendsData = await getRevenueTrends(
        token,
        '2024-01-01',
        '2024-12-31',
        'month'
      );
      setTrends(trendsData);
    };
    loadData();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {summary && (
        <div>
          <h2>Revenue</h2>
          <p>This Month: ${summary.revenue.this_month}</p>
          <p>Growth: {summary.revenue.growth_percent}%</p>
        </div>
      )}
      {/* Add charts for trends */}
    </div>
  );
}
```

### Step 8.3: Add Integration Configuration UI

Create a settings page for integrations:

```javascript
// IntegrationsSettings.jsx
async function configureERP(erpType, apiKey, baseUrl) {
  const response = await fetch('http://localhost:8000/api/v1/integrations/erp/configure', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      erp_type: erpType,
      api_key: apiKey,
      base_url: baseUrl
    })
  });
  return response.json();
}
```

---

## 9. Production Deployment

### Step 9.1: Environment Variables for Production

Create `backend/.env.production`:

```bash
# Security (USE STRONG VALUES!)
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET=<generate-strong-random-key>

# Database (Use production database)
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/unified_ai
REDIS_URL=redis://prod-redis-host:6379

# Application
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Production API keys
OPENAI_API_KEY=<production-key>
SENDGRID_API_KEY=<production-key>
ERP_API_KEY=<production-key>
```

**Generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 9.2: Database Migration

```bash
# Backup production database first!
pg_dump -U postgres unified_ai > backup.sql

# Run migrations
cd backend
alembic upgrade head
```

### Step 9.3: Deploy with Docker (Recommended)

```bash
# Build image
docker build -t unified-ai-backend .

# Run container
docker run -d \
  --name unified-ai \
  -p 8000:8000 \
  --env-file backend/.env.production \
  unified-ai-backend
```

### Step 9.4: Deploy with Systemd (Linux)

Create `/etc/systemd/system/unified-ai.service`:

```ini
[Unit]
Description=Unified AI Business Assistant API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/unified-ai/backend
Environment="PATH=/opt/unified-ai/backend/venv/bin"
ExecStart=/opt/unified-ai/backend/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable unified-ai
sudo systemctl start unified-ai
sudo systemctl status unified-ai
```

### Step 9.5: Configure Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Step 9.6: SSL Certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d api.yourdomain.com
```

### Step 9.7: Monitoring & Logging

Set up monitoring:
- **Application logs:** `backend/logs/combined.log`
- **Error logs:** `backend/logs/error.log`
- **System monitoring:** Use tools like Prometheus, Grafana, or Datadog

---

## 🔍 Verification Checklist

After completing all steps, verify:

- [ ] Backend server starts without errors
- [ ] Database connection works
- [ ] Redis connection works
- [ ] All API endpoints respond correctly
- [ ] Analytics endpoints return data
- [ ] Caching is working (check Redis)
- [ ] Integrations can be configured
- [ ] ML models load and make predictions
- [ ] Frontend can connect to backend
- [ ] Production environment variables are set
- [ ] Security keys are changed from defaults
- [ ] Database migrations are up to date
- [ ] Logs are being written correctly

---

## 🆘 Troubleshooting

### Common Issues

**1. Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping

# Check Redis URL in .env
echo $REDIS_URL
```

**2. Database Connection Error**
```bash
# Test PostgreSQL connection
psql -U postgres -d unified_ai -c "SELECT 1;"

# Check DATABASE_URL in .env
```

**3. ML Model Loading Error**
```bash
# Verify models exist
ls -la backend/ml/models/*/model.pkl

# Retrain if missing
python ml/scripts/train_all_models.py
```

**4. Integration API Errors**
- Verify API keys are correct
- Check API endpoint URLs
- Review integration service logs
- Test API connectivity manually

**5. Caching Not Working**
- Verify Redis is running
- Check cache TTL settings
- Review cache key generation
- Check Redis memory limits

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs
- **Implementation Guide:** `IMPROVEMENTS_IMPLEMENTED.md`
- **Project Summary:** `PROJECT_SUMMARY.md`

---

**Last Updated:** December 20, 2024

