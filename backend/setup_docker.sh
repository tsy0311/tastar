#!/bin/bash

# Setup script for PostgreSQL and Redis using Docker Compose
# This script sets up the required infrastructure services for the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

print_info "Setting up PostgreSQL and Redis with Docker Compose..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed."
    echo ""
    echo "Please install Docker:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: https://www.docker.com/products/docker-desktop"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Linux: https://docs.docker.com/engine/install/"
    else
        echo "  Visit: https://www.docker.com/products/docker-desktop"
    fi
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in project root."
    exit 1
fi

# Stop existing containers if they exist
print_info "Checking for existing containers..."
if $DOCKER_COMPOSE_CMD ps | grep -q "unified-ai-postgres\|unified-ai-redis"; then
    print_warning "Existing containers found. Stopping them..."
    $DOCKER_COMPOSE_CMD down 2>/dev/null || true
fi

# Start services
print_info "Starting Docker Compose services..."
if ! $DOCKER_COMPOSE_CMD up -d; then
    print_error "Failed to start Docker Compose services."
    exit 1
fi

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 3

# Check PostgreSQL health
print_info "Checking PostgreSQL health..."
POSTGRES_READY=false
for i in {1..30}; do
    if $DOCKER_COMPOSE_CMD exec -T postgres pg_isready -U postgres &> /dev/null; then
        POSTGRES_READY=true
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start after 30 seconds"
        echo ""
        echo "Checking logs..."
        $DOCKER_COMPOSE_CMD logs postgres | tail -20
        exit 1
    fi
    sleep 1
done

if [ "$POSTGRES_READY" = true ]; then
    print_success "PostgreSQL is ready!"
fi

# Check Redis health
print_info "Checking Redis health..."
REDIS_READY=false
for i in {1..30}; do
    if $DOCKER_COMPOSE_CMD exec -T redis redis-cli ping &> /dev/null; then
        REDIS_READY=true
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis failed to start after 30 seconds"
        echo ""
        echo "Checking logs..."
        $DOCKER_COMPOSE_CMD logs redis | tail -20
        exit 1
    fi
    sleep 1
done

if [ "$REDIS_READY" = true ]; then
    print_success "Redis is ready!"
fi

# Display service status
echo ""
print_info "Service Status:"
$DOCKER_COMPOSE_CMD ps

echo ""
print_success "Docker services are running!"
echo ""

# Display connection information
echo "📋 Connection Information:"
echo "  ┌─────────────────────────────────────────┐"
echo "  │ PostgreSQL:                              │"
echo "  │   Host:     localhost                    │"
echo "  │   Port:     5432                         │"
echo "  │   Database: unified_ai                   │"
echo "  │   User:     postgres                     │"
echo "  │   Password: postgres                     │"
echo "  └─────────────────────────────────────────┘"
echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │ Redis:                                    │"
echo "  │   Host:     localhost                    │"
echo "  │   Port:     6379                         │"
echo "  └─────────────────────────────────────────┘"
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    print_warning ".env file not found in backend directory."
    if [ -f "backend/.env.example" ]; then
        echo ""
        echo "You can create .env from the example:"
        echo "  cp backend/.env.example backend/.env"
    fi
fi

echo ""
echo "📝 Next Steps:"
echo "  1. Set up environment variables (copy backend/.env.example to backend/.env)"
echo "  2. Install Python dependencies:"
echo "     cd backend && ./install.sh"
echo "  3. Run database migrations:"
echo "     cd backend && source venv/bin/activate && alembic upgrade head"
echo "  4. (Optional) Seed the database:"
echo "     python scripts/seed_db.py"
echo "  5. Start the application:"
echo "     python run.py"
echo ""
echo "To stop services: docker compose down"
echo "To view logs: docker compose logs -f"




