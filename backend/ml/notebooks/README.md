# ML Notebooks Setup Guide

## Problem: scikit-learn Installation Error

If you see `ERROR: Failed to build 'scikit-learn'`, you're likely using system Python instead of the project's virtual environment.

## Quick Fix

### Option 1: Use the Virtual Environment (Recommended)

1. **Activate the venv:**
   ```bash
   cd backend
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Set up Jupyter kernel for venv:**
   ```bash
   # Make sure you're in the venv
   pip install ipykernel
   python -m ipykernel install --user --name=tastar --display-name="Python (tastar venv)"
   ```

3. **Start Jupyter:**
   ```bash
   jupyter notebook
   # or
   jupyter lab
   ```

4. **Select the correct kernel:**
   - In Jupyter: Kernel → Change Kernel → "Python (tastar venv)"
   - In JupyterLab: Click kernel name in top right → "Python (tastar venv)"

### Option 2: Install Dependencies in System Python (Not Recommended)

If you must use system Python, install build dependencies first:

**macOS:**
```bash
xcode-select --install
brew install gcc gfortran
pip install --upgrade pip setuptools wheel
pip install scikit-learn
```

**Linux:**
```bash
sudo apt-get install build-essential gfortran
pip install --upgrade pip setuptools wheel
pip install scikit-learn
```

## Verify Setup

Run this in a notebook cell:

```python
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

# Should show venv path, not system Python
import sklearn
print(f"scikit-learn: {sklearn.__version__}")
```

## Troubleshooting

### "Module not found" errors

Make sure you selected the correct kernel (tastar venv).

### Still getting build errors

1. Check Python version:
   ```bash
   python --version
   # Should be 3.11, 3.12, or 3.14 (not 3.15 alpha)
   ```

2. Use pre-built wheels only:
   ```bash
   pip install scikit-learn --only-binary :all:
   ```

3. Try a different version:
   ```bash
   pip install "scikit-learn>=1.5.0,<2.0.0"
   ```

## Recommended Workflow

1. Always activate venv before working:
   ```bash
   cd backend
   source venv/bin/activate
   ```

2. Install all dependencies once:
   ```bash
   pip install -r requirements.txt
   ```

3. Use venv kernel in Jupyter notebooks

4. Never install packages in system Python for this project
