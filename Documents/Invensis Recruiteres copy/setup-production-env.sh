#!/bin/bash

# 🚀 Invensis Hiring Portal - Production Environment Setup Script
# This script helps you set up production environment variables

set -e

echo "🚀 Setting up Production Environment Variables..."
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

# Create main production environment file
print_info "Creating main production environment file..."

cat > .env.production << 'EOF'
# Production Environment Configuration
# Invensis Hiring Portal Production Settings

# Database Configuration
MONGODB_URI=mongodb+srv://pmonishreddy19:<db_password>@cluster0.7m6bwkx.mongodb.net/invensis-recruiters?retryWrites=true&w=majority&appName=Cluster0

# JWT Configuration
JWT_SECRET=invensis-hiring-portal-super-secure-jwt-secret-2024
ADMIN_JWT_SECRET=invensis-admin-portal-super-secure-jwt-secret-2024

# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Server Configuration
PORT=5001
ADMIN_PORT=5002

# Frontend URLs (Production)
FRONTEND_URL=https://hiring.invensis.com
ADMIN_URL=https://admin.invensis.com

# CORS Configuration
CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com

# Environment
NODE_ENV=production
EOF

print_status "Main production environment file created"

# Create admin production environment file
print_info "Creating admin production environment file..."

cat > admin-portal/admin-server/.env.production << 'EOF'
# Admin Server Production Environment Configuration

# Database Configuration
MONGODB_URI=mongodb+srv://pmonishreddy19:<db_password>@cluster0.7m6bwkx.mongodb.net/invensis-recruiters?retryWrites=true&w=majority&appName=Cluster0

# JWT Configuration
ADMIN_JWT_SECRET=invensis-admin-portal-super-secure-jwt-secret-2024

# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Server Configuration
ADMIN_PORT=5002

# Frontend URLs (Production)
FRONTEND_URL=https://hiring.invensis.com
ADMIN_URL=https://admin.invensis.com

# CORS Configuration
CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com

# Environment
NODE_ENV=production
EOF

print_status "Admin production environment file created"

echo ""
echo "📋 Next Steps:"
echo "=================================================="
echo "1. Replace <db_password> with your actual MongoDB password"
echo "2. Update EMAIL_USER and EMAIL_PASS with your Gmail credentials"
echo "3. Test the connection to MongoDB Atlas"
echo "4. Deploy to production using ./deploy-production.sh"
echo ""
echo "🔧 To test MongoDB connection:"
echo "   node -e \"require('mongoose').connect('your-mongodb-uri').then(() => console.log('✅ Connected')).catch(e => console.log('❌ Failed:', e.message))\""
echo ""
echo "📚 For deployment instructions, see DEPLOYMENT_GUIDE.md"
echo "" 