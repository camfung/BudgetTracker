#!/bin/bash
# Production dependency installation script

set -e  # Exit on error

echo "🔧 Installing GeminiPay Budget App dependencies..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   It's recommended to activate a virtual environment first:"
    echo "   source .venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing Python packages..."

# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify critical packages
echo "✅ Verifying critical packages..."

python -c "import aiosqlite; print('✓ aiosqlite:', aiosqlite.__version__)" 2>/dev/null || {
    echo "❌ aiosqlite not found. Installing..."
    pip install aiosqlite>=0.19.0
}

python -c "import sqlalchemy; print('✓ sqlalchemy:', sqlalchemy.__version__)" 2>/dev/null || {
    echo "❌ sqlalchemy not found. Installing..."
    pip install "sqlalchemy[asyncio]>=2.0.0"
}

python -c "import fastapi; print('✓ fastapi:', fastapi.__version__)" 2>/dev/null || {
    echo "❌ fastapi not found. Installing..."
    pip install "fastapi>=0.100.0"
}

python -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)" 2>/dev/null || {
    echo "❌ uvicorn not found. Installing..."
    pip install "uvicorn[standard]>=0.23.0"
}

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To start the application:"
echo "  python main.py"
echo ""
echo "Or with uvicorn:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"