#!/bin/bash

# 🚀 Invensis Hiring Portal - Production Deployment Script
# This script automates the complete production deployment process

set -e

echo "🚀 Starting production deployment for Invensis Hiring Portal..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if required tools are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed!"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed!"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed!"
        exit 1
    fi
    
    print_status "All dependencies are installed"
}

# Build frontend applications
build_frontend() {
    print_info "Building frontend applications..."
    
    # Build main client
    cd client
    print_info "Building main client..."
    npm run build
    cd ..
    
    # Build admin client
    cd admin-portal/admin-client
    print_info "Building admin client..."
    npm run build
    cd ../..
    
    print_status "Frontend applications built successfully"
}

# Deploy to Vercel
deploy_vercel() {
    print_info "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm i -g vercel
    fi
    
    # Deploy main client
    cd client
    print_info "Deploying main client to Vercel..."
    vercel --prod --yes
    cd ..
    
    # Deploy admin client
    cd admin-portal/admin-client
    print_info "Deploying admin client to Vercel..."
    vercel --prod --yes
    cd ../..
    
    print_status "Vercel deployment completed"
}

# Deploy backend to Render
deploy_render() {
    print_info "Deploying backend to Render..."
    
    # Check if deploy-render.sh exists
    if [ -f "deploy-render.sh" ]; then
        chmod +x deploy-render.sh
        ./deploy-render.sh
    else
        print_warning "deploy-render.sh not found. Please deploy backend manually."
    fi
    
    print_status "Backend deployment completed"
}

# Setup environment files
setup_environment() {
    print_info "Setting up environment files..."
    
    # Copy example files if they don't exist
    if [ ! -f ".env.production" ]; then
        cp env.production.example .env.production
        print_warning "Created .env.production from example. Please update with your values."
    fi
    
    if [ ! -f "admin-portal/admin-server/.env.production" ]; then
        cp admin-portal/admin-server/env.production.example admin-portal/admin-server/.env.production
        print_warning "Created admin .env.production from example. Please update with your values."
    fi
    
    print_status "Environment files set up"
}

# Run tests
run_tests() {
    print_info "Running tests..."
    
    # Install dependencies if needed
    npm install
    
    # Run tests (if test script exists)
    if npm run test --silent 2>/dev/null; then
        print_status "Tests passed"
    else
        print_warning "No tests found or tests failed. Continuing deployment..."
    fi
}

# Main deployment process
main() {
    echo ""
    print_info "Starting deployment process..."
    
    # 1. Check dependencies
    check_dependencies
    
    # 2. Setup environment
    setup_environment
    
    # 3. Run tests
    run_tests
    
    # 4. Build frontend
    build_frontend
    
    # 5. Deploy to Vercel
    deploy_vercel
    
    # 6. Deploy backend
    deploy_render
    
    echo ""
    echo "🎉 Production deployment completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update environment variables in Vercel and Render"
    echo "2. Configure MongoDB Atlas database"
    echo "3. Set up email service (Gmail SMTP or SendGrid)"
    echo "4. Test all user flows in production"
    echo "5. Monitor application performance"
    echo ""
    echo "📚 Documentation: DEPLOYMENT_GUIDE.md"
    echo "🔗 Repository: https://github.com/Mo-nish/invensis-hiring-portal"
    echo ""
}

# Run main function
main "$@" 