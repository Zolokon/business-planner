#!/bin/bash
# Installation and startup script for Business Planner
# Run this on the server: nohup ./install_and_run.sh > install.log 2>&1 &

set -e

echo "======================================"
echo "Installing Business Planner"
echo "======================================"
echo ""

cd /root/business-planner

# Install dependencies in venv
echo "[1/3] Installing Python dependencies..."
echo "This may take 5-10 minutes..."
venv/bin/pip install --upgrade pip setuptools wheel
venv/bin/pip install fastapi uvicorn[standard] sqlalchemy asyncpg
venv/bin/pip install python-telegram-bot openai
venv/bin/pip install pydantic pydantic-settings
venv/bin/pip install python-decouple structlog
venv/bin/pip install redis aioredis httpx aiohttp
venv/bin/pip install pgvector alembic
echo "✓ Dependencies installed"
echo ""

# Test imports
echo "[2/3] Testing imports..."
venv/bin/python -c "import fastapi, uvicorn, sqlalchemy, asyncpg, telegram, openai; print('✓ All imports successful')"
echo ""

# Start the application
echo "[3/3] Starting application..."
echo "Application will run on http://0.0.0.0:8000"
echo ""

# Start with nohup
nohup venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
APP_PID=$!

echo "✓ Application started with PID: $APP_PID"
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Check status:"
echo "  tail -f /root/business-planner/app.log"
echo ""
echo "Test endpoints:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/businesses"
echo ""
echo "Stop application:"
echo "  kill $APP_PID"
echo ""
