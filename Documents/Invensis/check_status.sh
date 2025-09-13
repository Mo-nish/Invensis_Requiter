#!/bin/bash

echo "🔍 Checking Invensis Hiring Portal Status..."

# Check if port 5001 is in use
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "✅ Application is RUNNING on port 5001"
    echo "🌐 Main Site: http://localhost:5001"
    echo "🔧 Admin Portal: http://localhost:5001/admin/login"
    echo "📊 Cluster Dashboard: http://localhost:5001/cluster/dashboard"
    echo "👥 HR Dashboard: http://localhost:5001/hr/dashboard"
    echo "👨‍💼 Manager Dashboard: http://localhost:5001/manager/dashboard"
else
    echo "❌ Application is NOT RUNNING"
    echo "💡 To start the application, run: ./start_app.sh"
fi

echo ""
echo "📋 Process Information:"
lsof -i:5001 2>/dev/null || echo "No processes found on port 5001"
