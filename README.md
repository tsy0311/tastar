# Unified AI Business Assistant

A comprehensive, cloud-based enterprise application designed to consolidate all office operations for a CNC factory into a single, intelligent platform.

## 🚀 Features

- **AI Accounting System** - Automated invoice generation, document OCR, three-way matching
- **AI Purchasing Assistant** - Demand forecasting, automated PO generation, inventory optimization
- **AI Sales Assistant** - AI-powered quotations, intelligent pricing, opportunity management
- **AI Email & Chatbot** - 24/7 conversational AI, automated email responses

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ and npm 9+ (for frontend)
- PostgreSQL 15+
- Redis (for caching)
- Docker and Docker Compose (optional, for development)

## 🛠️ Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tsy0311/tastar.git
   cd tastar
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies** (when frontend is ready)
   ```bash
   cd frontend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

5. **Start database and Redis** (Choose one option)

   **Option A: Using Docker (Recommended)**
   ```bash
   # For newer Docker versions (Docker Desktop)
   docker compose up -d postgres redis
   
   # For older Docker versions
   docker-compose up -d postgres redis
   ```
   
   **Option B: Manual Installation (Without Docker)**
   - **PostgreSQL**: Install from https://www.postgresql.org/download/
     - Create database: `createdb unified_ai`
     - Or use pgAdmin to create database
   - **Redis**: Install from https://redis.io/download/
     - Windows: Use WSL2 or download from https://github.com/microsoftarchive/redis/releases
     - Or use Redis Cloud (free tier): https://redis.com/try-free/
   
   **Option C: Use Cloud Services**
   - PostgreSQL: Use services like Supabase, Neon, or Railway (free tiers available)
   - Redis: Use Redis Cloud or Upstash (free tiers available)
   - Update `DATABASE_URL` and `REDIS_URL` in `.env` file

6. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

7. **Seed database (optional)**
   ```bash
   python scripts/seed_db.py
   ```

8. **Start development servers**
   ```bash
   # Backend (from backend directory)
   python run.py
   # Or: uvicorn app.main:app --reload
   
   # Frontend (when ready)
   cd frontend && npm run dev
   ```

   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Frontend App: http://localhost:3000 (when ready)

> **Note**: If you don't have Docker installed, see [SETUP_WITHOUT_DOCKER.md](backend/SETUP_WITHOUT_DOCKER.md) for manual setup instructions or use cloud services (Supabase, Redis Cloud).

## 📁 Project Structure

```
tastar/
├── backend/          # Node.js/Express API server
├── frontend/         # React/TypeScript frontend
├── docs/             # Documentation
├── docker-compose.yml # Development services
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run backend tests only
npm run test:backend

# Run frontend tests only
npm run test:frontend
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [System Design](./docs/01-System-Design-Document.md)
- [API Specification](./docs/04-API-Specification.md)
- [Database Schema](./docs/03-Database-Schema.md)
- [Deployment Guide](./docs/09-Deployment-Guide.md)
- [Quick Start Guides](./docs/11-Quick-Start-Guides.md)

## 🏗️ Architecture

- **Frontend:** React 18, TypeScript, Material-UI
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy
- **Database:** PostgreSQL 15+
- **Cache:** Redis
- **AI/ML:** OpenAI GPT-4, Anthropic Claude, PyTorch, scikit-learn, Transformers

## 📝 License

Proprietary - All rights reserved

## 👥 Contributing

See [Development Phases](./docs/06-Development-Phases.md) for project roadmap and contribution guidelines.

