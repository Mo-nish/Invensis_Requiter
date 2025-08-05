#!/bin/bash

# Invensis Hiring Portal - Production Deployment Script
# This script helps deploy the application to production

set -e

echo "🚀 Starting Invensis Hiring Portal Production Deployment..."
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

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_error ".env.production file not found!"
    echo "Please copy env.production.example to .env.production and update with your production values."
    exit 1
fi

print_status "Environment file found"

# Clean up test data
echo ""
echo "🧹 Cleaning up test data..."
node cleanup-test-data.js

print_status "Test data cleanup completed"

# Build the React app for production
echo ""
echo "🔨 Building React app for production..."
cd client
npm run build
cd ..

print_status "React app built successfully"

# Install production dependencies
echo ""
echo "📦 Installing production dependencies..."
npm ci --only=production

print_status "Dependencies installed"

# Create production start script
echo ""
echo "📝 Creating production start script..."
cat > start-production.sh << 'EOF'
#!/bin/bash

# Production start script
export NODE_ENV=production

# Start main server
echo "🚀 Starting main server on port 5001..."
node server/index.js &

# Start admin server
echo "🚀 Starting admin server on port 5002..."
cd admin-portal/admin-server
node index.js &
cd ../..

# Wait for servers to start
sleep 5

echo "✅ All servers started successfully!"
echo "📊 Main Portal: http://localhost:5001"
echo "👑 Admin Portal: http://localhost:5002"

# Keep script running
wait
EOF

chmod +x start-production.sh

print_status "Production start script created"

# Create PM2 ecosystem file for process management
echo ""
echo "📝 Creating PM2 ecosystem file..."
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'invensis-main-server',
      script: 'server/index.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 5001
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 5001
      }
    },
    {
      name: 'invensis-admin-server',
      script: 'admin-portal/admin-server/index.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        ADMIN_PORT: 5002
      },
      env_production: {
        NODE_ENV: 'production',
        ADMIN_PORT: 5002
      }
    }
  ]
};
EOF

print_status "PM2 ecosystem file created"

# Create nginx configuration
echo ""
echo "📝 Creating nginx configuration..."
cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name hiring.invensis.com;

    # Main application
    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API routes
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 80;
    server_name admin.invensis.com;

    # Admin portal
    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Admin API routes
    location /api/admin/ {
        proxy_pass http://localhost:5002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

print_status "Nginx configuration created"

# Create deployment instructions
echo ""
echo "📝 Creating deployment instructions..."
cat > DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# Production Deployment Instructions

## Prerequisites
- Node.js 18+ installed
- MongoDB Atlas account (or other cloud database)
- Domain names configured (hiring.invensis.com, admin.invensis.com)
- SSL certificates for HTTPS

## Step 1: Environment Setup
1. Copy `env.production.example` to `.env.production`
2. Update with your production values:
   - MongoDB connection string
   - JWT secrets
   - Email credentials
   - Domain URLs

## Step 2: Database Setup
1. Create MongoDB Atlas cluster
2. Get connection string
3. Update MONGODB_URI in .env.production

## Step 3: Email Setup
1. Create Gmail app password
2. Update EMAIL_USER and EMAIL_PASS in .env.production

## Step 4: Domain & SSL
1. Configure DNS for hiring.invensis.com and admin.invensis.com
2. Install SSL certificates (Let's Encrypt recommended)

## Step 5: Server Deployment
1. Upload code to server
2. Run: `npm install`
3. Run: `node cleanup-test-data.js`
4. Run: `cd client && npm run build`
5. Start with PM2: `pm2 start ecosystem.config.js`

## Step 6: Nginx Configuration
1. Copy nginx.conf to /etc/nginx/sites-available/
2. Enable site: `ln -s /etc/nginx/sites-available/invensis /etc/nginx/sites-enabled/`
3. Test: `nginx -t`
4. Reload: `systemctl reload nginx`

## Step 7: Testing
1. Test main portal: https://hiring.invensis.com
2. Test admin portal: https://admin.invensis.com
3. Test email invitations
4. Test user registration flow

## Monitoring
- PM2 logs: `pm2 logs`
- Nginx logs: `/var/log/nginx/`
- Application logs: Check PM2 output

## Backup
- Database: MongoDB Atlas provides automatic backups
- Code: Use Git repository
- Environment: Keep .env.production secure

## Security Checklist
- [ ] JWT secrets are strong and unique
- [ ] Database connection uses SSL
- [ ] Email credentials are secure
- [ ] SSL certificates are valid
- [ ] Firewall rules are configured
- [ ] Regular security updates
EOF

print_status "Deployment instructions created"

echo ""
echo "🎉 Deployment preparation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env.production with your production values"
echo "2. Set up your production server"
echo "3. Configure domain names and SSL"
echo "4. Run the deployment instructions"
echo ""
echo "📚 See DEPLOYMENT_INSTRUCTIONS.md for detailed steps"
echo "" 