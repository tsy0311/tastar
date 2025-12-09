# PowerShell script to install Python dependencies
# Usage: .\install.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan

