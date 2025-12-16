# Quick Start Guide

## Fastest Setup (Using Cloud Services - No Installation Needed)

1. **Get Free Cloud Services**:
   - PostgreSQL: Sign up at [Supabase](https://supabase.com) (free tier)
   - Redis: Sign up at [Redis Cloud](https://redis.com/try-free/) (free tier)

2. **Install Python Dependencies**:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```powershell
   Copy-Item .env.example .env
   # Edit .env and add your cloud service URLs
   ```

4. **Run Migrations**:
   ```powershell
   alembic upgrade head
   ```

5. **Start Server**:
   ```powershell
   python run.py
   ```

Done! Visit http://localhost:8000/api/docs

## With Docker (If Installed)

```bash
# Start services
docker compose up -d postgres redis

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
python run.py
```

## Without Docker (Local Installation)

See [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md) for detailed instructions.




