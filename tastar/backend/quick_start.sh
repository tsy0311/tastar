#!/bin/bash
# Quick start script - Fastest way to get the application running
# Assumes you've already run setup.sh or have everything configured

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Start - Unified AI Business Assistant${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup first...${NC}\n"
    bash setup.sh
    exit 0
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created. Please edit it with your configuration.${NC}\n"
    fi
fi

# Quick health check
if [ -f "scripts/check_health.py" ]; then
    echo -e "${BLUE}🔍 Quick health check...${NC}"
    python scripts/check_health.py --quiet 2>/dev/null || echo -e "${YELLOW}⚠️  Some services may not be ready${NC}\n"
fi

# Start the application
echo -e "${GREEN}🚀 Starting application...${NC}\n"
echo -e "${BLUE}Access the API at: http://localhost:8000${NC}"
echo -e "${BLUE}API Docs at: http://localhost:8000/api/docs${NC}\n"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

python run.py


