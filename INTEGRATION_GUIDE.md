# Complete Integration Guide: PostgreSQL & Redis with Docker Compose

## Overview

This guide will help you set up PostgreSQL and Redis using Docker Compose to enable full functionality of the Unified AI Business Assistant application.

## Current Status

✅ **Completed:**
- Python 3.14.2 installed
- Virtual environment created
- Dependencies installed (except torch/transformers - not needed for core functionality)
- Application running (without database/Redis)

⏳ **Next Steps:**
- Install Docker Desktop
- Start PostgreSQL and Redis containers
- Run database migrations
- Verify full functionality

## Step-by-Step Setup

### Step 1: Install Docker Desktop

1. Download Docker Desktop for macOS:
   - Visit: https://www.docker.com/products/docker-desktop
   - Download the version for your Mac (Intel or Apple Silicon)
   - Install the `.dmg` file

2. Start Docker Desktop:
   - Open Docker Desktop from Applications
   - Wait for it to start (whale icon in menu bar should be steady)

3. Verify installation:
   ```bash
   docker --version
   docker compose version
   ```

### Step 2: Start Docker Services

From the project root directory:

```bash
# Navigate to project root
cd /Users/ads/Documents/Tastar/tastar

# Start services in detached mode
docker compose up -d
```

This will:
- Pull PostgreSQL 15 and Redis 7 images (if not already downloaded)
- Create containers: `unified-ai-postgres` and `unified-ai-redis`
- Start services on ports 5432 (PostgreSQL) and 6379 (Redis)
- Create persistent volumes for data

### Step 3: Verify Services are Running

```bash
# Check service status
docker compose ps

# You should see both services with "healthy" or "running" status
```

Expected output:
```
NAME                    STATUS
unified-ai-postgres     Up (healthy)
unified-ai-redis        Up (healthy)
```

### Step 4: Test Connections

```bash
# Test PostgreSQL
docker compose exec postgres pg_isready -U postgres
# Should output: postgres:5432 - accepting connections

# Test Redis
docker compose exec redis redis-cli ping
# Should output: PONG
```

### Step 5: Create Database Migration

```bash
cd backend
source venv/bin/activate

# Create initial migration from models
alembic revision --autogenerate -m "Initial migration"
```

This will create a migration file in `backend/alembic/versions/` with all your database tables.

### Step 6: Run Migrations

```bash
# Apply migrations to create tables
alembic upgrade head
```

This will create all database tables:
- companies
- users
- roles
- user_roles
- customers
- invoices
- invoice_line_items
- payments
- payment_allocations

### Step 7: (Optional) Seed Initial Data

```bash
# Seed database with sample data
python scripts/seed_db.py
```

### Step 8: Restart Application

The application should automatically connect to PostgreSQL and Redis. If it's already running, restart it:

```bash
# Stop current instance (if running)
pkill -f "python run.py"

# Start fresh
python run.py
```

### Step 9: Verify Full Functionality

1. **Check Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"ok","version":"1.0.0"}`

2. **Check API Documentation:**
   - Open browser: http://localhost:8000/api/docs
   - You should see all API endpoints

3. **Test Database Connection:**
   - Try creating a user or company via the API
   - Check that data persists

## Quick Setup Script

For automated setup, use the provided script:

```bash
cd backend
./setup_docker.sh
```

This script will:
- Check if Docker is installed and running
- Start Docker Compose services
- Wait for services to be ready
- Display service status
- Provide next steps

## Docker Compose Configuration

Your `docker-compose.yml` is configured with:

### PostgreSQL Service
```yaml
- Image: postgres:15-alpine
- Container: unified-ai-postgres
- Port: 5432:5432
- Database: unified_ai
- User: postgres
- Password: postgres
- Volume: postgres_data (persistent)
```

### Redis Service
```yaml
- Image: redis:7-alpine
- Container: unified-ai-redis
- Port: 6379:6379
- Volume: redis_data (persistent)
```

## Connection Strings

The application uses these default connection strings:

- **PostgreSQL**: `postgresql://postgres:postgres@localhost:5432/unified_ai`
- **Redis**: `redis://localhost:6379`

These are defined in `backend/app/core/config.py` and match the Docker Compose configuration.

## Useful Docker Commands

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs postgres
docker compose logs redis

# Follow logs in real-time
docker compose logs -f postgres
```

### Service Management
```bash
# Stop services (keeps containers)
docker compose stop

# Start services
docker compose start

# Restart services
docker compose restart

# Stop and remove containers (keeps data volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

### Database Access
```bash
# Access PostgreSQL CLI
docker compose exec postgres psql -U postgres -d unified_ai

# Run SQL commands
docker compose exec postgres psql -U postgres -d unified_ai -c "SELECT COUNT(*) FROM companies;"

# Access Redis CLI
docker compose exec redis redis-cli

# Redis commands
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli keys "*"
```

## Troubleshooting

### Issue: Docker not found
**Solution:** Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Issue: Port already in use
**Error:** `Bind for 0.0.0.0:5432 failed: port is already allocated`

**Solution:**
```bash
# Find what's using the port
lsof -i :5432
lsof -i :6379

# Stop the conflicting service or change ports in docker-compose.yml
```

### Issue: Connection refused
**Error:** `connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused`

**Solution:**
1. Check if Docker is running: `docker info`
2. Check if containers are running: `docker compose ps`
3. Check container logs: `docker compose logs postgres`
4. Restart services: `docker compose restart`

### Issue: Migration fails
**Error:** `relation "alembic_version" does not exist`

**Solution:**
```bash
# This is normal for first migration - just run it again
alembic upgrade head
```

### Issue: Database connection in app fails
**Solution:**
1. Verify Docker services are running: `docker compose ps`
2. Check connection string matches: `postgresql://postgres:postgres@localhost:5432/unified_ai`
3. Test connection manually:
   ```bash
   docker compose exec postgres psql -U postgres -d unified_ai -c "SELECT 1;"
   ```

## Verification Checklist

After setup, verify:

- [ ] Docker Desktop is installed and running
- [ ] `docker compose ps` shows both services as "healthy"
- [ ] PostgreSQL accepts connections: `docker compose exec postgres pg_isready -U postgres`
- [ ] Redis responds: `docker compose exec redis redis-cli ping`
- [ ] Migration created: `ls backend/alembic/versions/` shows migration file
- [ ] Migration applied: `alembic upgrade head` completes successfully
- [ ] Application starts without database errors
- [ ] Health endpoint works: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/api/docs

## Next Steps After Setup

1. **Create initial admin user** (via API or seed script)
2. **Configure environment variables** in `.env` file if needed
3. **Set up backups** for production
4. **Monitor logs** for any issues
5. **Test all API endpoints** via Swagger UI

## Production Considerations

For production deployment:

1. **Change default passwords** in `docker-compose.yml`
2. **Use environment variables** for sensitive data
3. **Set up automated backups** for PostgreSQL
4. **Configure Redis persistence** (already configured)
5. **Use Docker secrets** or external secret management
6. **Set up monitoring** (Prometheus, Grafana)
7. **Use reverse proxy** (nginx, traefik)
8. **Enable SSL/TLS** for database connections

## Support

If you encounter issues:

1. Check service logs: `docker compose logs`
2. Verify Docker is running: `docker info`
3. Check service health: `docker compose ps`
4. Review the `DOCKER_SETUP.md` file for detailed troubleshooting

## Summary

Once you complete these steps:

✅ PostgreSQL running on port 5432  
✅ Redis running on port 6379  
✅ Database tables created  
✅ Application fully functional  
✅ All API endpoints working  

Your application is now ready for development and testing! 🎉

