# Unified AI Business Assistant - Backend

Python/FastAPI backend for the Unified AI Business Assistant application.

## Features

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **JWT Authentication** - Secure token-based auth
- **ML/AI Ready** - Integrated with OpenAI, Anthropic, and ML libraries

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or cloud database like Supabase)
- Redis (or cloud Redis like Redis Cloud)

> **Quick Start**: See [QUICK_START.md](QUICK_START.md) for the fastest setup options.

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Seed database (optional)**
   ```bash
   python scripts/seed_db.py
   ```

6. **Run development server**
   ```bash
   python run.py
   # Or
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Default Credentials

After seeding:
- Email: `admin@demo.com`
- Password: `admin123`

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/    # API endpoints
│   │       └── router.py     # Main router
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   ├── logging.py        # Logging setup
│   │   └── security.py       # Security utilities
│   ├── database/
│   │   ├── connection.py     # Database connection
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   └── main.py               # FastAPI app
├── alembic/                  # Database migrations
├── scripts/                  # Utility scripts
└── requirements.txt          # Python dependencies
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## ML/AI Integration

The backend includes ML libraries ready for:
- **OpenAI GPT-4** - For NLP and text generation
- **Anthropic Claude** - Alternative LLM
- **PyTorch** - Deep learning models
- **scikit-learn** - Traditional ML
- **Transformers** - Hugging Face models

See `app/services/` for ML service implementations (to be added).

