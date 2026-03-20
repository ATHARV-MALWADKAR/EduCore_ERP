#!/bin/bash

# College ERP - Backend Startup Script

clear
echo "========================================"
echo "College ERP - Backend Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

python3 --version
echo "[✓] Python found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "[✓] Virtual environment created"
    echo ""
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null
if [ -f venv/bin/activate ]; then
    echo "[✓] Virtual environment activated"
fi

# Install/upgrade requirements
echo ""
echo "Installing dependencies (this may take a minute)..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi
echo "[✓] Dependencies installed"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

echo "========================================"
echo "Starting College ERP Backend Server"
echo "========================================"
echo ""
echo "URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Login: http://localhost:8000/login"
echo ""
echo "Default Credentials:"
echo "  Email: admin@college.edu"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
