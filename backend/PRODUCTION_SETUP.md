# Production Setup Guide

## Quick Fix for SQLAlchemy Async Error

If you're getting the error:
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'pysqlite' is not async.
```

### Solution 1: Install Missing Dependencies (Recommended)

```bash
# Navigate to backend directory
cd /root/BudgetTracker/backend

# Activate virtual environment
source .venv/bin/activate

# Install aiosqlite for async SQLite support
pip install aiosqlite>=0.19.0

# Or install all requirements
pip install -r requirements.txt

# Run the app
python main.py
```

### Solution 2: Use Installation Script

```bash
cd /root/BudgetTracker/backend
source .venv/bin/activate
chmod +x scripts/install_deps.sh
./scripts/install_deps.sh
```

### Solution 3: Manual Verification

Check if aiosqlite is installed:
```bash
source .venv/bin/activate
python -c "import aiosqlite; print(f'aiosqlite version: {aiosqlite.__version__}')"
```

If not installed:
```bash
pip install aiosqlite
```

## Environment Variables

Create `.env` file in `/root/BudgetTracker/backend/`:

```env
# Database (SQLite with async support)
DATABASE_URL=sqlite+aiosqlite:///./budget_app.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (for frontend)
ALLOWED_ORIGINS=["https://budget.camfung.dev", "http://localhost:5173"]

# Production settings
DEBUG=False
LOG_LEVEL=INFO
```

## Required Packages

The app requires these critical packages:
- `aiosqlite>=0.19.0` - Async SQLite driver
- `sqlalchemy[asyncio]>=2.0.0` - Async SQLAlchemy
- `fastapi>=0.100.0` - Web framework
- `uvicorn[standard]>=0.23.0` - ASGI server

## Running the App

```bash
# Method 1: Direct Python
python main.py

# Method 2: Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Method 3: With specific config
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

### Common Issues:

1. **aiosqlite not found**: `pip install aiosqlite`
2. **Permission denied**: `chmod +x scripts/install_deps.sh`
3. **Module not found**: Ensure virtual environment is activated
4. **Database locked**: Check if another instance is running

### Logs and Debugging:

```bash
# Check Python path
python -c "import sys; print(sys.executable)"

# List installed packages
pip list

# Check app imports
python -c "from models.database import engine; print('Database OK')"
```