#!/bin/bash
# Bash script to install Python dependencies
# Usage: ./install.sh

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

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    echo "Please install Python 3.11 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    print_error "Python 3.11 or higher is required. Found: Python $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in current directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install requirements
print_info "Installing Python dependencies..."
print_warning "This may take a few minutes..."

if pip install -r requirements.txt; then
    print_success "All dependencies installed successfully"
else
    print_error "Failed to install some dependencies"
    echo ""
    echo "Common issues:"
    echo "  - Check your internet connection"
    echo "  - Some packages may require system dependencies"
    echo "  - On macOS, you may need: xcode-select --install"
    echo "  - On Linux, you may need: build-essential, python3-dev"
    exit 1
fi

# Verify installation
print_info "Verifying installation..."
if python -c "import fastapi, sqlalchemy, redis" 2>/dev/null; then
    print_success "Core packages verified"
else
    print_warning "Some packages may not be installed correctly"
fi

echo ""
print_success "Installation complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Set up environment variables:"
echo "     cp .env.example .env"
echo "     # Edit .env with your configuration"
echo ""
echo "  3. Set up database (if using Docker):"
echo "     cd .. && ./setup_docker.sh"
echo ""
echo "  4. Run database migrations:"
echo "     alembic upgrade head"
echo ""
echo "  5. (Optional) Seed the database:"
echo "     python scripts/seed_db.py"
echo ""
echo "  6. Start the application:"
echo "     python run.py"
echo ""






