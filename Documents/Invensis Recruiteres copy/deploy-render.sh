#!/bin/bash

# Invensis Hiring Portal - Render Deployment Script
# This script prepares the backend applications for Render deployment

set -e

echo "🚀 Preparing Render Deployment for Invensis Hiring Portal..."
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

# Create Render configuration files
echo ""
echo "📝 Creating Render configuration files..."

# Hiring Server Render configuration
cat > render-hiring.yaml << 'EOF'
services:
  - type: web
    name: invensis-hiring-server
    env: node
    plan: free
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 10000
      - key: MONGODB_URI
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: EMAIL_USER
        sync: false
      - key: EMAIL_PASS
        sync: false
      - key: FRONTEND_URL
        value: https://hiring.invensis.com
      - key: CORS_ORIGIN
        value: https://hiring.invensis.com,https://admin.invensis.com
    routes:
      - type: rewrite
        source: /api/hiring/*
        destination: /api/*
EOF

print_status "Hiring server Render config created"

# Admin Server Render configuration
cat > render-admin.yaml << 'EOF'
services:
  - type: web
    name: invensis-admin-server
    env: node
    plan: free
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: ADMIN_PORT
        value: 10000
      - key: MONGODB_URI
        sync: false
      - key: ADMIN_JWT_SECRET
        sync: false
      - key: EMAIL_USER
        sync: false
      - key: EMAIL_PASS
        sync: false
      - key: ADMIN_URL
        value: https://admin.invensis.com
      - key: CORS_ORIGIN
        value: https://hiring.invensis.com,https://admin.invensis.com
    routes:
      - type: rewrite
        source: /api/admin/*
        destination: /api/admin/*
EOF

print_status "Admin server Render config created"

# Create deployment instructions
cat > RENDER_DEPLOYMENT.md << 'EOF'
# Render Deployment Instructions

## Prerequisites
- Render account (free tier available)
- MongoDB Atlas account
- Domain names configured

## Step 1: Deploy Hiring Server
1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: invensis-hiring-server
   - Root Directory: (leave empty)
   - Environment: Node
   - Build Command: npm install
   - Start Command: npm start
   - Plan: Free

5. Add Environment Variables:
   - NODE_ENV: production
   - PORT: 10000
   - MONGODB_URI: (your MongoDB Atlas URL)
   - JWT_SECRET: (your secret key)
   - EMAIL_USER: (your Gmail)
   - EMAIL_PASS: (your app password)
   - FRONTEND_URL: https://hiring.invensis.com
   - CORS_ORIGIN: https://hiring.invensis.com,https://admin.invensis.com

6. Deploy and note the URL (e.g., https://invensis-hiring-server.onrender.com)

## Step 2: Deploy Admin Server
1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: invensis-admin-server
   - Root Directory: admin-portal/admin-server
   - Environment: Node
   - Build Command: npm install
   - Start Command: npm start
   - Plan: Free

5. Add Environment Variables:
   - NODE_ENV: production
   - ADMIN_PORT: 10000
   - MONGODB_URI: (your MongoDB Atlas URL)
   - ADMIN_JWT_SECRET: (your admin secret key)
   - EMAIL_USER: (your Gmail)
   - EMAIL_PASS: (your app password)
   - ADMIN_URL: https://admin.invensis.com
   - CORS_ORIGIN: https://hiring.invensis.com,https://admin.invensis.com

6. Deploy and note the URL (e.g., https://invensis-admin-server.onrender.com)

## Step 3: Configure Custom Domains
1. In Render dashboard, go to each service
2. Click "Settings" → "Custom Domains"
3. Add:
   - api.invensis.com/hiring → hiring server
   - api.invensis.com/admin → admin server

## Step 4: Update Frontend Configuration
1. Update Vercel environment variables:
   - REACT_APP_API_URL: https://api.invensis.com/hiring (for hiring portal)
   - REACT_APP_API_URL: https://api.invensis.com/admin (for admin portal)

## Step 5: Test Deployment
1. Test hiring portal: https://hiring.invensis.com
2. Test admin portal: https://admin.invensis.com
3. Test API endpoints:
   - https://api.invensis.com/hiring/api/auth/login
   - https://api.invensis.com/admin/api/admin/auth/login

## Monitoring
- Check Render logs for any errors
- Monitor MongoDB Atlas for database connections
- Test email functionality

## Backup
- Render provides automatic backups
- MongoDB Atlas provides database backups
- Keep environment variables secure
EOF

print_status "Render deployment instructions created"

echo ""
echo "🎉 Render deployment preparation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy hiring server to Render using render-hiring.yaml"
echo "2. Deploy admin server to Render using render-admin.yaml"
echo "3. Configure custom domains in Render dashboard"
echo "4. Update frontend API URLs"
echo "5. Test the complete deployment"
echo ""
echo "📚 See RENDER_DEPLOYMENT.md for detailed steps"
echo "" 