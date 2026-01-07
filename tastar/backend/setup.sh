#!/bin/bash
# Comprehensive setup script for Unified AI Business Assistant
# This script orchestrates the complete setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "🚀 Unified AI Business Assistant - Setup Script"

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    echo "Please install Python 3.11 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    print_success "Docker found (optional)"
else
    print_warning "Docker not found (optional, but recommended for database setup)"
fi

# Step 2: Setup Docker services (if Docker is available)
print_header "Step 2: Setting up Infrastructure Services"

if command -v docker &> /dev/null && docker info &> /dev/null; then
    read -p "Do you want to set up PostgreSQL and Redis using Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setting up Docker services..."
        cd ..
        if [ -f "setup_docker.sh" ]; then
            bash setup_docker.sh
        else
            print_warning "setup_docker.sh not found, skipping Docker setup"
        fi
        cd "$SCRIPT_DIR"
    else
        print_info "Skipping Docker setup. Make sure PostgreSQL and Redis are running."
    fi
else
    print_warning "Docker not available. Make sure PostgreSQL and Redis are running."
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis: localhost:6379"
fi

# Step 3: Setup environment variables
print_header "Step 3: Setting up Environment Variables"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file from .env.example..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your configuration"
        echo ""
        read -p "Press Enter to continue after editing .env (or skip to use defaults)..."
    else
        print_warning ".env.example not found. Using default configuration."
    fi
else
    print_success ".env file already exists"
fi

# Step 4: Install Python dependencies
print_header "Step 4: Installing Python Dependencies"

if [ -f "install.sh" ]; then
    print_info "Running install.sh..."
    bash install.sh
else
    print_warning "install.sh not found, installing dependencies manually..."
    
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -r requirements.txt
    print_success "Dependencies installed"
fi

# Step 5: Validate environment
print_header "Step 5: Validating Environment"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    if [ -f "scripts/validate_env.py" ]; then
        print_info "Validating environment variables..."
        python scripts/validate_env.py || print_warning "Environment validation had warnings"
    fi
else
    print_warning "Virtual environment not found, skipping validation"
fi

# Step 6: Run database migrations
print_header "Step 6: Running Database Migrations"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    if command -v alembic &> /dev/null; then
        print_info "Running database migrations..."
        if alembic upgrade head; then
            print_success "Database migrations completed"
        else
            print_error "Database migrations failed"
            echo "Make sure PostgreSQL is running and DATABASE_URL is correct"
        fi
    else
        print_warning "Alembic not found. Install it with: pip install alembic"
    fi
else
    print_warning "Virtual environment not found, skipping migrations"
fi

# Step 7: Optional database seeding
print_header "Step 7: Database Seeding (Optional)"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    if [ -f "scripts/seed_db.py" ]; then
        read -p "Do you want to seed the database with sample data? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Seeding database..."
            if python scripts/seed_db.py; then
                print_success "Database seeded successfully"
            else
                print_warning "Database seeding failed (non-critical)"
            fi
        fi
    fi
fi

# Step 8: Health check
print_header "Step 8: Running Health Check"

if [ -f "venv/bin/activate" ] && [ -f "scripts/check_health.py" ]; then
    source venv/bin/activate
    print_info "Running health check..."
    python scripts/check_health.py || print_warning "Some health checks failed"
fi

# Final summary
print_header "🎉 Setup Complete!"

print_success "Setup process completed!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the application:"
echo "   python run.py"
echo ""
echo "3. Access the API documentation:"
echo "   http://localhost:8000/api/docs"
echo ""
echo "4. (Optional) Run health check anytime:"
echo "   python scripts/check_health.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


