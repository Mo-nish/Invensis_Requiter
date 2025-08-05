#!/bin/bash

# 🚀 Invensis Hiring Portal - Quick Start Script
# This script helps you get the development environment running quickly

set -e

echo "🚀 Starting Invensis Hiring Portal..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Kill any existing processes
cleanup() {
    print_info "Cleaning up existing processes..."
    pkill -f "node" 2>/dev/null || true
    pkill -f "nodemon" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    sleep 2
}

# Check if ports are available
check_ports() {
    print_info "Checking port availability..."
    
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 5001 is in use. Killing process..."
        lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    fi
    
    if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 5002 is in use. Killing process..."
        lsof -ti:5002 | xargs kill -9 2>/dev/null || true
    fi
    
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 3000 is in use. Killing process..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
    
    print_status "Ports are available"
}

# Install dependencies
install_deps() {
    print_info "Installing dependencies..."
    
    # Root dependencies
    npm install
    
    # Client dependencies
    cd client && npm install && cd ..
    
    # Admin client dependencies
    cd admin-portal/admin-client && npm install && cd ../..
    
    # Admin server dependencies
    cd admin-portal/admin-server && npm install && cd ../..
    
    print_status "Dependencies installed"
}

# Start development servers
start_dev() {
    print_info "Starting development servers..."
    
    # Start main server and client
    npm run dev &
    
    # Start admin server
    cd admin-portal/admin-server && npm start &
    cd ../..
    
    # Wait for servers to start
    sleep 5
    
    print_status "Development servers started"
}

# Check server health
check_health() {
    print_info "Checking server health..."
    
    # Check main server
    if curl -s http://localhost:5001/api/health > /dev/null; then
        print_status "Main server is running on http://localhost:5001"
    else
        print_error "Main server is not responding"
    fi
    
    # Check admin server
    if curl -s http://localhost:5002/api/admin/health > /dev/null; then
        print_status "Admin server is running on http://localhost:5002"
    else
        print_error "Admin server is not responding"
    fi
    
    # Check client
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Client is running on http://localhost:3000"
    else
        print_error "Client is not responding"
    fi
}

# Show URLs
show_urls() {
    echo ""
    echo "🌐 Application URLs:"
    echo "=================================================="
    echo "📱 Main Hiring Portal: http://localhost:3000"
    echo "👑 Admin Portal: http://localhost:3002"
    echo "🔧 Main API: http://localhost:5001"
    echo "🔧 Admin API: http://localhost:5002"
    echo ""
    echo "📋 Default Test Accounts:"
    echo "=================================================="
    echo "Admin: admin@invensis.com / password123"
    echo "HR: hr@invensis.com / password123"
    echo "Manager: manager@invensis.com / password123"
    echo "Board: board@invensis.com / password123"
    echo ""
    echo "📚 Documentation:"
    echo "=================================================="
    echo "📖 Deployment Guide: DEPLOYMENT_GUIDE.md"
    echo "🔗 GitHub: https://github.com/Mo-nish/invensis-hiring-portal"
    echo ""
    echo "🛠️  Development Commands:"
    echo "=================================================="
    echo "📦 Install deps: npm run install-all"
    echo "🚀 Start dev: npm run dev"
    echo "🏗️  Build: npm run build"
    echo "🧪 Test: npm test"
    echo "🔧 Deploy: ./deploy-production.sh"
    echo ""
}

# Main function
main() {
    echo ""
    print_info "Starting Invensis Hiring Portal setup..."
    
    # 1. Cleanup
    cleanup
    
    # 2. Check ports
    check_ports
    
    # 3. Install dependencies
    install_deps
    
    # 4. Start development servers
    start_dev
    
    # 5. Check health
    check_health
    
    # 6. Show URLs
    show_urls
    
    echo "🎉 Setup completed! Your development environment is ready."
    echo ""
    echo "💡 Tip: Press Ctrl+C to stop all servers"
    echo ""
}

# Run main function
main "$@" 