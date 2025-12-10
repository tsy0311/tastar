# Docker Setup Guide for PostgreSQL and Redis

This guide will help you set up PostgreSQL and Redis using Docker Compose for full application functionality.

## Prerequisites

1. **Docker Desktop** - Install from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Python 3.14.2** - Already installed ✅
3. **Virtual Environment** - Already set up ✅

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd backend
./setup_docker.sh
```

### Option 2: Manual Setup

#### Step 1: Start Docker Services

From the project root directory:

```bash
docker compose up -d
```

This will start:
- **PostgreSQL** on port `5432`
- **Redis** on port `6379`

#### Step 2: Verify Services are Running

```bash
docker compose ps
```

You should see both `postgres` and `redis` services with status "healthy" or "running".

#### Step 3: Check Service Health

```bash
# Check PostgreSQL
docker compose exec postgres pg_isready -U postgres

# Check Redis
docker compose exec redis redis-cli ping
```

#### Step 4: Run Database Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

This will create all the necessary database tables.

#### Step 5: (Optional) Seed Initial Data

```bash
python scripts/seed_db.py
```

#### Step 6: Start the Application

```bash
python run.py
```

The application will now connect to:
- **PostgreSQL**: `postgresql://postgres:postgres@localhost:5432/unified_ai`
- **Redis**: `redis://localhost:6379`

## Docker Compose Configuration

The `docker-compose.yml` file is already configured with:

### PostgreSQL
- **Image**: `postgres:15-alpine`
- **Container**: `unified-ai-postgres`
- **Port**: `5432:5432`
- **Database**: `unified_ai`
- **User**: `postgres`
- **Password**: `postgres`
- **Volume**: `postgres_data` (persistent storage)

### Redis
- **Image**: `redis:7-alpine`
- **Container**: `unified-ai-redis`
- **Port**: `6379:6379`
- **Volume**: `redis_data` (persistent storage)

## Useful Commands

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs postgres
docker compose logs redis

# Follow logs
docker compose logs -f
```

### Stop Services
```bash
docker compose stop
```

### Start Services
```bash
docker compose start
```

### Restart Services
```bash
docker compose restart
```

### Stop and Remove Services (keeps data)
```bash
docker compose down
```

### Stop and Remove Everything (including data)
```bash
docker compose down -v
```

### Access PostgreSQL CLI
```bash
docker compose exec postgres psql -U postgres -d unified_ai
```

### Access Redis CLI
```bash
docker compose exec redis redis-cli
```

## Environment Variables

The application uses these default connection strings (defined in `backend/app/core/config.py`):

- **DATABASE_URL**: `postgresql://postgres:postgres@localhost:5432/unified_ai`
- **REDIS_URL**: `redis://localhost:6379`

You can override these by creating a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/unified_ai
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Troubleshooting

### Port Already in Use

If you get an error that port 5432 or 6379 is already in use:

1. Check what's using the port:
   ```bash
   lsof -i :5432
   lsof -i :6379
   ```

2. Stop the conflicting service or change the port in `docker-compose.yml`

### Database Connection Failed

1. Ensure Docker services are running:
   ```bash
   docker compose ps
   ```

2. Check service logs:
   ```bash
   docker compose logs postgres
   ```

3. Verify the connection string matches the Docker Compose configuration

### Reset Database

If you need to start fresh:

```bash
# Stop and remove containers and volumes
docker compose down -v

# Start services again
docker compose up -d

# Run migrations
cd backend
source venv/bin/activate
alembic upgrade head
```

## Production Considerations

For production, you should:

1. **Change default passwords** in `docker-compose.yml`
2. **Use environment variables** for sensitive data
3. **Set up proper backups** for PostgreSQL
4. **Configure Redis persistence** if needed
5. **Use Docker secrets** or external secret management
6. **Set up monitoring** and health checks
7. **Use a reverse proxy** (nginx, traefik) for production

## Next Steps

Once Docker services are running:

1. ✅ Run migrations: `alembic upgrade head`
2. ✅ (Optional) Seed data: `python scripts/seed_db.py`
3. ✅ Start application: `python run.py`
4. ✅ Access API docs: http://localhost:8000/api/docs

Your application is now fully functional with PostgreSQL and Redis! 🎉

