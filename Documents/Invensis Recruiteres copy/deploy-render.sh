#!/bin/bash

# Render Deployment Script for Invensis Hiring Portal
echo "🚀 Starting Render deployment..."

# Check if we're in the right directory
if [ ! -d "server" ]; then
    echo "❌ Error: server directory not found!"
    exit 1
fi

# Check if server/package.json exists
if [ ! -f "server/package.json" ]; then
    echo "❌ Error: server/package.json not found!"
    exit 1
fi

echo "✅ Directory structure looks good"

# Test the build locally first
echo "🔧 Testing build locally..."
cd server
npm install
if [ $? -ne 0 ]; then
    echo "❌ Local build failed!"
    exit 1
fi

echo "✅ Local build successful"

# Go back to root
cd ..

echo "📋 Render Configuration:"
echo "   Root Directory: (leave empty)"
echo "   Build Command: cd server && npm install"
echo "   Start Command: cd server && npm start"
echo ""
echo "🔧 Environment Variables needed:"
echo "   NODE_ENV=production"
echo "   PORT=10000"
echo "   MONGODB_URI=your-mongodb-atlas-connection-string"
echo "   JWT_SECRET=your-secure-jwt-secret"
echo "   EMAIL_USER=your-gmail-address"
echo "   EMAIL_PASS=your-gmail-app-password"
echo "   FRONTEND_URL=https://hiring.invensis.com"
echo "   CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com"
echo ""
echo "🎯 Ready to deploy to Render!"
echo "   1. Go to Render Dashboard"
echo "   2. Create new Web Service"
echo "   3. Connect to: https://github.com/Mo-nish/invensis-hiring-portal"
echo "   4. Use the configuration above"
echo "   5. Deploy!" 