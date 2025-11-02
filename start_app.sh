#!/bin/bash

echo "🚀 Starting Invensis Hiring Portal..."

# Kill any existing processes on port 5001
echo "🔧 Checking for existing processes on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

# Activate virtual environment and start the application
echo "📦 Activating virtual environment..."
source .venv/bin/activate

echo "🌐 Starting Flask application..."
echo "✅ Application will be available at: http://localhost:5001"
echo "✅ Admin Portal: http://localhost:5001/admin/login"
echo "✅ Press Ctrl+C to stop the application"
echo "=================================================="

python run.py
