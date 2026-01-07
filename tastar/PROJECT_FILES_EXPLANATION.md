# Project Files Explanation

Complete guide to all files in the Unified AI Business Assistant project.

## 📁 Project Structure Overview

```
tastar/
├── backend/          # FastAPI backend application
├── frontend/         # Electron desktop application
├── docs/             # Documentation directory
├── docker-compose.yml
├── package.json
└── MANUAL_IMPLEMENTATION_GUIDE.md
```

---

## 🔧 Root Level Files

### Configuration Files

**`docker-compose.yml`**
- Docker Compose configuration for running PostgreSQL and Redis
- Defines services, networks, and volumes
- Usage: `docker compose up -d`

**`package.json`** (Root)
- Workspace package configuration
- Defines workspace scripts and dependencies
- Used for managing the monorepo structure

**`build-exe.js`**
- Script for building the Electron desktop application
- Configures Electron Builder settings
- Creates standalone .exe installer

**`MANUAL_IMPLEMENTATION_GUIDE.md`**
- Comprehensive manual setup and configuration guide
- Step-by-step instructions for all manual tasks
- Troubleshooting and verification checklists

---

## 🐍 Backend Directory (`backend/`)

### Core Application Files

**`run.py`**
- Main entry point for the FastAPI application
- Starts the Uvicorn server
- Handles command-line arguments and server configuration

**`requirements.txt`**
- Python package dependencies
- Includes FastAPI, SQLAlchemy, ML libraries, etc.
- Install with: `pip install -r requirements.txt`

**`pyproject.toml`**
- Python project configuration
- Build system settings
- Project metadata

**`alembic.ini`**
- Alembic database migration configuration
- Database connection settings
- Migration script location

**`Makefile`**
- Common development commands
- Shortcuts for setup, testing, and deployment

### Setup & Installation Scripts

**`setup.sh`**
- Unix/Linux setup script
- Installs dependencies and sets up environment

**`setup_docker.sh`**
- Docker environment setup script
- Configures Docker containers

**`install.sh`**
- Installation script for Unix systems
- Sets up Python virtual environment

**`install.ps1`**
- PowerShell installation script for Windows
- Sets up Python virtual environment on Windows

**`quick_start.sh`**
- Quick start script for development
- Starts all required services

### Utility Scripts (`backend/scripts/`)

**`check_health.py`**
- Health check utility
- Verifies database and Redis connections
- Checks system status

**`validate_env.py`**
- Environment variable validation
- Ensures all required variables are set
- Validates configuration

**`seed_db.py`**
- Database seeding script
- Populates database with initial data
- Creates demo/test data

### Logs Directory (`backend/logs/`)

**`combined.log`**
- Combined application logs
- All log levels (INFO, WARNING, ERROR)

**`error.log`**
- Error-only logs
- Critical errors and exceptions

---

## 🎯 Application Core (`backend/app/`)

### Main Application

**`main.py`**
- FastAPI application initialization
- Middleware configuration (CORS, GZip)
- API router inclusion
- Lifespan management (startup/shutdown)

**`__init__.py`**
- Python package initialization
- Makes `app` a Python package

### Core Module (`backend/app/core/`)

**`config.py`**
- Application configuration settings
- Environment variable management
- Settings for database, Redis, JWT, AI services, integrations
- Uses Pydantic Settings for validation

**`security.py`**
- Security utilities
- JWT token encoding/decoding
- Password hashing (bcrypt)
- Token validation

**`dependencies.py`**
- FastAPI dependencies
- `get_current_user` - Authenticates users from JWT
- `get_current_active_user` - Validates active users
- `require_role` - Role-based access control

**`logging.py`**
- Logging configuration
- Loguru setup
- Log file rotation
- Log formatting

**`cache.py`**
- Redis caching utilities
- `@cached` decorator for function result caching
- Cache key generation
- Cache invalidation functions
- Cache statistics

**`query_optimizer.py`**
- Database query optimization utilities
- Eager loading for relationships
- Batch querying
- Query statistics
- Index creation helpers

**`tenant_middleware.py`**
- Multi-tenant support middleware
- Tenant ID extraction from headers/query params
- Tenant access validation
- Automatic query filtering by company_id
- Tenant context manager

### Database Module (`backend/app/database/`)

**`connection.py`**
- Database connection management
- SQLAlchemy engine creation
- Session factory
- Connection pooling
- Async database initialization

**`models.py`**
- SQLAlchemy database models
- All table definitions:
  - Company, User, Role, Customer, Supplier
  - Invoice, Payment, Bill, PurchaseOrder, Quotation
  - Material, Document
- Relationships and constraints
- Indexes for performance

**`cms_models.py`**
- CMS (Content Management System) models
- Custom field definitions
- Flexible field management
- Dynamic form configuration

**`redis_client.py`**
- Redis client connection
- Async Redis operations
- Connection management
- Redis URL configuration

**`init_db.py`**
- Database initialization
- Table creation
- Initial data setup

**`migrations/__init__.py`**
- Alembic migrations package

**`seeds/__init__.py`**
- Database seeding package

### API Module (`backend/app/api/`)

**`v1/router.py`**
- Main API router
- Includes all endpoint routers
- API versioning (v1)
- Route organization by module

#### Endpoints (`backend/app/api/v1/endpoints/`)

**`auth.py`**
- Authentication endpoints
- Login, logout, token refresh
- User registration
- Password reset

**`users.py`**
- User management endpoints
- CRUD operations for users
- User profile management
- Role assignment

**`companies.py`**
- Company management endpoints
- Company CRUD operations
- Company settings
- Subscription management

**`customers.py`**
- Customer management endpoints
- Customer database operations
- Customer search and filtering
- Customer analytics

**`invoices.py`**
- Invoice management endpoints
- Invoice creation, update, deletion
- Invoice status management
- Invoice PDF generation

**`payments.py`**
- Payment tracking endpoints
- Payment recording
- Payment allocation to invoices
- Payment history

**`bills.py`**
- Bill/expense management endpoints
- Bill creation and management
- Vendor bill processing
- Bill approval workflow

**`suppliers.py`**
- Supplier management endpoints
- Supplier database operations
- Supplier performance tracking

**`materials.py`**
- Material/inventory management endpoints
- Material CRUD operations
- Stock level tracking
- Reorder point management

**`purchase_orders.py`**
- Purchase order endpoints
- PO creation and management
- PO status tracking
- Supplier communication

**`quotations.py`**
- Quotation management endpoints
- Quotation generation
- Quotation tracking
- Customer quotation management

**`documents.py`**
- Document management endpoints
- Document upload and storage
- OCR processing
- Document classification
- Document search

**`matching.py`**
- Three-way matching endpoints
- Invoice-PO-Receipt matching
- Matching validation
- Discrepancy handling

**`reports.py`**
- Financial reporting endpoints
- Aging receivables report
- Aging payables report
- Profit & Loss statement
- Balance sheet
- All reports use caching for performance

**`analytics.py`**
- Business intelligence endpoints
- Revenue trends analysis
- Customer analytics (CLV, retention)
- Sales forecasting
- Inventory analytics
- Dashboard summary
- All endpoints use Redis caching

**`integrations.py`**
- Third-party integration endpoints
- ERP system configuration and sync
- Accounting software integration
- Email service configuration
- Integration status checking

**`ai_assistant.py`**
- AI assistant endpoints
- Chat interface
- AI suggestions
- Autofill support

**`cms.py`**
- CMS endpoints
- Custom field management
- Dynamic form configuration
- Field definition CRUD

**`demo.py`**
- Demo data generation endpoints
- Test data creation
- Demo mode utilities

### Schemas Module (`backend/app/schemas/`)

Pydantic schemas for request/response validation:

**`auth.py`** - Authentication schemas (login, token)
**`user.py`** - User schemas
**`company.py`** - Company schemas
**`customer.py`** - Customer schemas
**`invoice.py`** - Invoice schemas
**`payment.py`** - Payment schemas
**`bill.py`** - Bill schemas
**`supplier.py`** - Supplier schemas
**`material.py`** - Material schemas
**`purchase_order.py`** - Purchase order schemas
**`quotation.py`** - Quotation schemas
**`matching.py`** - Matching schemas
**`cms.py`** - CMS field schemas

### Services Module (`backend/app/services/`)

**`ai_service.py`**
- AI service integration
- OpenAI GPT-4 integration
- Anthropic Claude integration
- AI text generation

**`ai_suggestion_service.py`**
- AI autofill suggestions
- Context-aware suggestions
- Pattern recognition
- Field completion

**`ml_service.py`**
- Machine learning model service
- Loads trained ML models
- Document classification
- Sentiment analysis
- Entity extraction
- Invoice extraction
- Demand forecasting

**`document_service.py`**
- Document processing service
- OCR processing
- Document storage
- Document metadata management

**`integration_service.py`**
- Third-party integration service
- ERP integration (SAP, Oracle, NetSuite)
- Accounting software integration (QuickBooks, Xero)
- Email service integration (SendGrid, SMTP)
- Unified integration management

---

## 🤖 Machine Learning (`backend/ml/`)

### Data Directory (`backend/ml/data/`)

**`raw/`**
- Raw training datasets (CSV files):
  - `documents_combined.csv` - Document classification data
  - `sentiment_combined.csv` - Sentiment analysis data
  - `entity_extraction_combined.csv` - Entity extraction data
  - `invoice_extraction_combined.csv` - Invoice extraction data
  - `demand_forecasting_combined.csv` - Demand forecasting data

### Models Directory (`backend/ml/models/`)

Trained model files organized by model type:

**`document_classifier/`**
- `model.pkl` - Trained RandomForest classifier
- `vectorizer.pkl` - TF-IDF vectorizer
- `metadata.json` - Model performance metrics
- `confusion_matrix.png` - Confusion matrix visualization
- `feature_importance.png` - Feature importance plot
- `class_priors.png` - Class distribution

**`sentiment_analyzer/`**
- `model.pkl` - Trained MultinomialNB classifier
- `vectorizer.pkl` - TF-IDF vectorizer
- `metadata.json` - Model metrics
- `nb_confusion_matrix.png` - Confusion matrix
- `feature_importance.png` - Feature importance
- `class_priors.png` - Class distribution

**`entity_extractor/`**
- `rule_based_extractor.pkl` - Rule-based entity extractor
- `entity_extraction_demo.png` - Demo visualization

**`invoice_extractor/`**
- `invoice_extractor.pkl` - Invoice data extractor
- `invoice_extraction_demo.png` - Demo visualization

**`demand_forecaster/`**
- `model.pkl` - Trained Linear Regression model
- `metadata.json` - Model metrics
- `forecast.csv` - Forecast results
- `demand_history.png` - Historical demand visualization
- `ma_forecast.png` - Moving average forecast

### Scripts Directory (`backend/ml/scripts/`)

**`download_datasets.py`**
- Downloads training datasets from various sources
- Hugging Face datasets
- Kaggle datasets
- Local database extraction
- Synthetic data generation

**`modify_datasets.py`**
- Dataset preprocessing and improvement
- Text cleaning and normalization
- Feature engineering
- Label standardization
- Duplicate removal
- Class balancing

**`train_all_models.py`**
- Orchestrates training of all 5 ML models
- Sequential model training
- Error handling
- Training summary generation

**`train_document_classifier.py`**
- Trains document classification model
- RandomForest classifier
- TF-IDF vectorization
- Model evaluation and saving

**`train_sentiment_analyzer.py`**
- Trains sentiment analysis model
- MultinomialNB classifier
- Text preprocessing
- Model evaluation

**`train_entity_extractor.py`**
- Creates rule-based entity extractor
- Regex pattern matching
- Entity type definitions

**`train_invoice_extractor.py`**
- Creates invoice data extractor
- Rule-based extraction
- Field mapping

**`train_demand_forecaster.py`**
- Trains demand forecasting model
- Linear regression
- Time series features
- Forecast generation

**`hyperparameter_tuning.py`**
- Hyperparameter optimization
- GridSearchCV and RandomizedSearchCV
- Parameter grid definitions
- Best model selection

**`train_transformer_models.py`**
- Transformer model training (BERT, DistilBERT)
- Hugging Face Transformers
- Fine-tuning for document classification and sentiment
- Model checkpointing

**`generate_visualizations.py`**
- Generates all model visualizations
- Confusion matrices
- Feature importance plots
- Forecast charts
- Entity extraction demos

**`prepare_data.py`**
- Prepares training data from database
- Data extraction and formatting
- Export to CSV

### Utils Directory (`backend/ml/utils/`)

**`data_loader.py`**
- Dataset loading utilities
- CSV file reading
- Database data extraction
- Data format conversion

**`model_evaluator.py`**
- Model evaluation utilities
- Accuracy, precision, recall, F1
- Confusion matrix generation
- Classification reports

**`model_saver.py`**
- Model saving utilities
- Pickle serialization
- Metadata saving
- Model versioning

### Notebooks Directory (`backend/ml/notebooks/`)

Jupyter notebooks for interactive model development:

**`01_document_classification.ipynb`**
- Document classification training notebook
- Data exploration
- Model training
- Evaluation and visualization

**`02_sentiment_analysis.ipynb`**
- Sentiment analysis training notebook
- Text preprocessing
- Model comparison
- Performance analysis

**`03_entity_extraction.ipynb`**
- Entity extraction notebook
- NER model development
- Pattern matching

**`04_invoice_data_extraction.ipynb`**
- Invoice extraction notebook
- Field extraction techniques
- Validation

**`05_demand_forecasting.ipynb`**
- Demand forecasting notebook
- Time series analysis
- Forecast visualization

**`visualize_models.ipynb`**
- Model visualization notebook
- Performance metrics
- Comparison charts

---

## 🗄️ Database Migrations (`backend/alembic/`)

**`env.py`**
- Alembic environment configuration
- Database connection setup
- Migration script execution

**`script.py.mako`**
- Alembic migration template
- Used for generating new migrations

**`versions/`**
- Migration version files:
  - `e09dd2e69a00_initial_migration.py` - Initial database schema
  - `ceeffe76d8fd_add_cms_models_for_flexible_fields.py` - CMS models migration

---

## 🖥️ Frontend Directory (`frontend/`)

### Main Files

**`package.json`**
- Node.js dependencies
- Electron configuration
- Build scripts

**`electron-main.js`**
- Electron main process
- Application window management
- System integration

**`main.js`**
- Frontend application entry point
- DOM initialization
- Event handlers

**`preload.js`**
- Electron preload script
- Secure context bridge
- API exposure to renderer

**`index.html`**
- Main HTML file
- Application structure
- UI layout

**`installer.js`**
- Installation logic
- Dependency installation
- Setup wizard

### Source Files (`frontend/src/`)

**`app.js`**
- Main application logic
- UI initialization
- Component management

**`api.js`**
- API client
- HTTP request handling
- Authentication

**`ai-autofill.js`**
- AI autofill functionality
- Suggestion handling
- Tab-to-accept feature

**`dynamic-form.js`**
- Dynamic form generation
- CMS field rendering
- Form validation

**`cms-demo.js`**
- CMS demo functionality
- Field management UI

**`styles.css`**
- Application styles
- UI theming
- Responsive design

### Build Directory (`frontend/build/`)

**`Unified AI Assistant Setup 1.0.0.exe`**
- Windows installer executable
- Standalone application installer

**`win-unpacked/`**
- Unpacked application files
- Electron runtime
- Application resources

**`builder-debug.yml`**
- Electron Builder debug configuration

**`builder-effective-config.yaml`**
- Effective build configuration
- Build settings

---

## 📊 File Statistics

### By Type

- **Python Files:** ~150+ files
- **JavaScript Files:** ~10 files
- **Configuration Files:** ~15 files
- **Data Files:** 5 CSV datasets
- **Model Files:** 10+ .pkl files
- **Visualization Files:** 10 PNG files
- **Notebook Files:** 6 Jupyter notebooks

### By Function

- **API Endpoints:** 20 endpoint files
- **Database Models:** 1 main models file + CMS models
- **Services:** 5 service files
- **ML Scripts:** 12 training/utility scripts
- **Core Utilities:** 7 core module files
- **Schemas:** 13 Pydantic schema files

---

## 🔑 Key Files to Understand

### For Backend Development

1. **`backend/app/main.py`** - Application entry point
2. **`backend/app/core/config.py`** - Configuration management
3. **`backend/app/database/models.py`** - Database schema
4. **`backend/app/api/v1/router.py`** - API routing
5. **`backend/app/core/dependencies.py`** - Authentication

### For ML Development

1. **`backend/ml/scripts/train_all_models.py`** - Model training
2. **`backend/ml/utils/data_loader.py`** - Data loading
3. **`backend/app/services/ml_service.py`** - Model usage
4. **`backend/ml/scripts/hyperparameter_tuning.py`** - Optimization

### For Frontend Development

1. **`frontend/main.js`** - Application entry
2. **`frontend/src/app.js`** - Main logic
3. **`frontend/src/api.js`** - API communication
4. **`frontend/electron-main.js`** - Electron integration

### For Deployment

1. **`docker-compose.yml`** - Docker setup
2. **`backend/requirements.txt`** - Python dependencies
3. **`backend/alembic.ini`** - Database migrations
4. **`MANUAL_IMPLEMENTATION_GUIDE.md`** - Setup guide

---

## 📝 File Naming Conventions

### Python Files
- **Snake_case** for all Python files
- **Descriptive names** indicating purpose
- **Module organization** by functionality

### API Endpoints
- **Plural nouns** (e.g., `invoices.py`, `customers.py`)
- **One resource per file**
- **RESTful naming**

### Services
- **`*_service.py`** suffix for service files
- **Single responsibility** per service

### Scripts
- **`train_*.py`** for training scripts
- **`download_*.py`** for data scripts
- **`generate_*.py`** for generation scripts

---

## 🔄 File Dependencies

### Core Dependencies

```
main.py
  ├── config.py
  ├── logging.py
  ├── database/connection.py
  ├── database/redis_client.py
  └── api/v1/router.py
      └── endpoints/*.py
          ├── schemas/*.py
          ├── services/*.py
          └── database/models.py
```

### ML Dependencies

```
ml_service.py
  └── ml/models/*/model.pkl
      └── ml/scripts/train_*.py
          └── ml/utils/*.py
              └── ml/data/raw/*.csv
```

---

## 📚 Additional Resources

- **API Documentation:** Available at `/api/docs` when server is running
- **Manual Setup:** See `MANUAL_IMPLEMENTATION_GUIDE.md`
- **Code Comments:** All files include inline documentation
- **Type Hints:** Python files use type annotations

---

**Last Updated:** December 20, 2024


