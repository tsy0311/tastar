# Setup Without Docker

This guide helps you set up the backend without Docker.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or cloud database)
- Redis (or cloud Redis service)

## Step 1: Install PostgreSQL

### Windows

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. PostgreSQL will run as a Windows service automatically

### Create Database

Open PowerShell or Command Prompt and run:

```powershell
# Connect to PostgreSQL (use the password you set during installation)
psql -U postgres

# In psql, create the database
CREATE DATABASE unified_ai;

# Exit psql
\q
```

Or use pgAdmin (GUI tool that comes with PostgreSQL):
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `unified_ai`
4. Click "Save"

## Step 2: Install Redis

### Option A: Using WSL2 (Recommended for Windows)

```bash
# In WSL2 terminal
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Option B: Download Windows Build

1. Download from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

### Option C: Use Redis Cloud (Easiest)

1. Sign up at: https://redis.com/try-free/
2. Create a free database
3. Copy the connection URL
4. Update `REDIS_URL` in `.env` file

## Step 3: Configure Environment

1. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and update:
   ```env
   # Database - use your PostgreSQL credentials
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/unified_ai
   
   # Redis - use your Redis connection
   REDIS_URL=redis://localhost:6379
   # Or if using Redis Cloud:
   # REDIS_URL=redis://username:password@host:port
   ```

## Step 4: Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Run Database Migrations

```powershell
# Make sure PostgreSQL is running
alembic upgrade head
```

## Step 6: Seed Database (Optional)

```powershell
python scripts/seed_db.py
```

## Step 7: Start the Server

```powershell
python run.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

## Troubleshooting

### PostgreSQL Connection Error

- Make sure PostgreSQL service is running:
  ```powershell
  # Check service status
  Get-Service postgresql*
  
  # Start service if stopped
  Start-Service postgresql-x64-15  # Adjust version number
  ```

- Verify connection:
  ```powershell
  psql -U postgres -d unified_ai
  ```

### Redis Connection Error

- If using local Redis, make sure it's running:
  ```bash
  # In WSL2
  redis-cli ping
  # Should return: PONG
  ```

- If using Redis Cloud, verify the connection URL in `.env`

### Port Already in Use

If port 8000 is already in use, change it in `.env`:
```env
PORT=8001
```

## Alternative: Use Cloud Services

### PostgreSQL Options

1. **Supabase** (Free tier): https://supabase.com
   - Create project → Get connection string
   - Update `DATABASE_URL` in `.env`

2. **Neon** (Free tier): https://neon.tech
   - Create database → Get connection string
   - Update `DATABASE_URL` in `.env`

3. **Railway** (Free tier): https://railway.app
   - Deploy PostgreSQL → Get connection string
   - Update `DATABASE_URL` in `.env`

### Redis Options

1. **Redis Cloud** (Free tier): https://redis.com/try-free/
   - Create database → Get connection URL
   - Update `REDIS_URL` in `.env`

2. **Upstash** (Free tier): https://upstash.com
   - Create database → Get connection URL
   - Update `REDIS_URL` in `.env`

## Quick Start with Cloud Services

1. Sign up for Supabase (PostgreSQL) and Redis Cloud
2. Get connection strings
3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host:port/db
   REDIS_URL=redis://user:pass@host:port
   ```
4. Run migrations and start server

No local installation needed!




