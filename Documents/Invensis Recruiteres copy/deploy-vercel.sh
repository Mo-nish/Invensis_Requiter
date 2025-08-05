#!/bin/bash

# Invensis Hiring Portal - Vercel Deployment Script
# This script deploys the frontend applications to Vercel

set -e

echo "🚀 Starting Vercel Deployment for Invensis Hiring Portal..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed!"
    echo "Please install it with: npm i -g vercel"
    exit 1
fi

print_status "Vercel CLI found"

# Deploy Hiring Portal Frontend
echo ""
echo "📦 Deploying Hiring Portal Frontend..."
cd client

# Create vercel.json for hiring portal
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://api.invensis.com/hiring"
  }
}
EOF

# Build the app
npm run build

# Deploy to Vercel
vercel --prod --name invensis-hiring-portal

print_status "Hiring Portal deployed successfully"

# Deploy Admin Portal Frontend
echo ""
echo "📦 Deploying Admin Portal Frontend..."
cd ../admin-portal/admin-client

# Create vercel.json for admin portal
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://api.invensis.com/admin"
  }
}
EOF

# Build the app
npm run build

# Deploy to Vercel
vercel --prod --name invensis-admin-portal

print_status "Admin Portal deployed successfully"

echo ""
echo "🎉 Vercel deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Configure custom domains in Vercel dashboard:"
echo "   - hiring.invensis.com → invensis-hiring-portal"
echo "   - admin.invensis.com → invensis-admin-portal"
echo "2. Update DNS records to point to Vercel"
echo "3. Deploy backend servers to Render/Railway"
echo "4. Update environment variables in Vercel dashboard"
echo ""
echo "📚 See DEPLOYMENT_INSTRUCTIONS.md for detailed steps"
echo "" 