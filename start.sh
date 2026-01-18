#!/bin/bash
# PhaseSentinel Startup Script

echo "🚀 Starting PhaseSentinel..."
echo "================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python version:"
python --version

# Navigate to backend directory
cd backend

# Check if requirements are installed
echo "✓ Checking dependencies..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p models
mkdir -p data

# Show status
echo ""
echo "================================"
echo "📊 PhaseSentinel Configuration"
echo "================================"
echo "✓ Backend: Flask API (http://localhost:5000)"
echo "✓ Frontend: Dashboard (http://localhost:5000/dashboard)"
echo "✓ Data directory: backend/data/"
echo "✓ Models directory: backend/models/"
echo ""
echo "Starting server..."
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

# Start the Flask server
python app.py
