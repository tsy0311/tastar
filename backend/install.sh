#!/bin/bash
# Bash script to install Python dependencies
# Usage: ./install.sh

echo "Installing Python dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"




