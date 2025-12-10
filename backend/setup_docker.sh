#!/bin/bash

# Setup script for PostgreSQL and Redis using Docker Compose

set -e

echo "🚀 Setting up PostgreSQL and Redis with Docker Compose..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop for macOS:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📦 Starting Docker Compose services..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check PostgreSQL health
echo "🔍 Checking PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start"
        exit 1
    fi
    sleep 1
done

# Check Redis health
echo "🔍 Checking Redis..."
for i in {1..30}; do
    if docker compose exec -T redis redis-cli ping &> /dev/null; then
        echo "✅ Redis is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Redis failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Docker services are running!"
echo ""
echo "Next steps:"
echo "1. Run database migrations: cd backend && source venv/bin/activate && alembic upgrade head"
echo "2. (Optional) Seed the database: python scripts/seed_db.py"
echo "3. Start the application: python run.py"
echo ""
echo "Services are available at:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Database: unified_ai"
echo "  - User: postgres"
echo "  - Password: postgres"

