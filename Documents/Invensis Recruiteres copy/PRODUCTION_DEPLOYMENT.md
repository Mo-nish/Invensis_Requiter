# Invensis Hiring Portal - Production Deployment Guide

## Overview
This guide covers deploying the Invensis Hiring Portal to production with two separate URLs:
- **Admin Portal**: https://admin.invensis.com
- **Hiring Portal**: https://hiring.invensis.com

## Prerequisites
- Domain names configured (admin.invensis.com, hiring.invensis.com)
- MongoDB Atlas account
- Gmail account with app password
- Vercel account (for frontend)
- Render/Railway account (for backend) OR VPS (AWS EC2/DigitalOcean)

## Option 1: Managed Deployment (Recommended)

### Step 1: Database Setup
1. Create MongoDB Atlas cluster
2. Get connection string
3. Create database user with read/write permissions

### Step 2: Frontend Deployment (Vercel)

#### Deploy Hiring Portal Frontend
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy hiring portal
cd client
vercel --prod --name invensis-hiring-portal
```

#### Deploy Admin Portal Frontend
```bash
cd admin-portal/admin-client
vercel --prod --name invensis-admin-portal
```

#### Configure Custom Domains in Vercel
1. Go to Vercel dashboard
2. For each project, go to Settings → Domains
3. Add custom domains:
   - hiring.invensis.com → invensis-hiring-portal
   - admin.invensis.com → invensis-admin-portal

### Step 3: Backend Deployment (Render)

#### Deploy Hiring Server
1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - Name: invensis-hiring-server
   - Root Directory: (leave empty)
   - Environment: Node
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Plan: Free

5. Add Environment Variables:
   ```
   NODE_ENV=production
   PORT=10000
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/invensis-recruiters
   JWT_SECRET=your-super-secure-jwt-secret-key-here
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   FRONTEND_URL=https://hiring.invensis.com
   CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com
   ```

#### Deploy Admin Server
1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - Name: invensis-admin-server
   - Root Directory: `admin-portal/admin-server`
   - Environment: Node
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Plan: Free

5. Add Environment Variables:
   ```
   NODE_ENV=production
   ADMIN_PORT=10000
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/invensis-recruiters
   ADMIN_JWT_SECRET=your-super-secure-admin-jwt-secret-key-here
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   ADMIN_URL=https://admin.invensis.com
   CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com
   ```

### Step 4: Configure Custom Domains in Render
1. In Render dashboard, go to each service
2. Click "Settings" → "Custom Domains"
3. Add:
   - api.invensis.com/hiring → hiring server
   - api.invensis.com/admin → admin server

### Step 5: Update Frontend API URLs
1. In Vercel dashboard, go to each project
2. Go to Settings → Environment Variables
3. Add:
   - `REACT_APP_API_URL`: `https://api.invensis.com/hiring` (for hiring portal)
   - `REACT_APP_API_URL`: `https://api.invensis.com/admin` (for admin portal)

## Option 2: VPS Deployment

### Step 1: Server Setup
1. Launch VPS (Ubuntu 20.04+)
2. Install Node.js, Nginx, PM2
3. Configure firewall

### Step 2: Application Deployment
```bash
# Clone repository
git clone <your-repo>
cd invensis-recruiters

# Install dependencies
npm run install-all

# Build frontend
cd client && npm run build
cd ../admin-portal/admin-client && npm run build

# Copy nginx configuration
sudo cp nginx-production.conf /etc/nginx/sites-available/invensis
sudo ln -s /etc/nginx/sites-available/invensis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: SSL Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificates
sudo certbot --nginx -d hiring.invensis.com
sudo certbot --nginx -d admin.invensis.com
sudo certbot --nginx -d api.invensis.com
```

### Step 4: PM2 Process Management
```bash
# Start applications with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Testing Checklist

### 1. Domain Configuration
- [ ] hiring.invensis.com resolves correctly
- [ ] admin.invensis.com resolves correctly
- [ ] SSL certificates are valid
- [ ] HTTP redirects to HTTPS

### 2. Frontend Testing
- [ ] Hiring portal loads at https://hiring.invensis.com
- [ ] Admin portal loads at https://admin.invensis.com
- [ ] No console errors
- [ ] Responsive design works

### 3. Backend Testing
- [ ] API endpoints respond correctly
- [ ] Database connections work
- [ ] Email sending works
- [ ] Role limits are enforced

### 4. User Flow Testing
- [ ] Admin can log in at admin.invensis.com
- [ ] Admin can add users with role limits
- [ ] Email invitations are sent with correct URLs
- [ ] Users can register via invitation links
- [ ] Users are redirected to correct dashboards
- [ ] Login/logout works for all roles

### 5. Security Testing
- [ ] JWT tokens work correctly
- [ ] CORS is configured properly
- [ ] Role-based access control works
- [ ] No sensitive data exposed

## Monitoring & Maintenance

### Logs
- Vercel: Check deployment logs in dashboard
- Render: Check service logs in dashboard
- VPS: `pm2 logs` and `/var/log/nginx/`

### Backups
- MongoDB Atlas: Automatic backups enabled
- Code: Git repository
- Environment variables: Keep secure copies

### Updates
- Monitor for security updates
- Test updates in staging environment
- Use blue-green deployment for zero downtime

## Troubleshooting

### Common Issues
1. **Port conflicts**: Use pre-start scripts in package.json
2. **Email not sending**: Check Gmail app password
3. **CORS errors**: Verify CORS_ORIGIN configuration
4. **Database connection**: Check MongoDB Atlas network access
5. **SSL issues**: Verify certificate installation

### Debug Commands
```bash
# Check server status
pm2 status
nginx -t
systemctl status nginx

# Check logs
pm2 logs
tail -f /var/log/nginx/error.log

# Test API endpoints
curl https://api.invensis.com/hiring/health
curl https://api.invensis.com/admin/health
```

## Security Checklist
- [ ] Strong JWT secrets
- [ ] HTTPS enabled everywhere
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Regular security updates
- [ ] Backup strategy in place

## Performance Optimization
- [ ] Enable gzip compression
- [ ] Configure caching headers
- [ ] Optimize images
- [ ] Use CDN for static assets
- [ ] Monitor response times

## Support
For deployment issues:
1. Check logs for error messages
2. Verify environment variables
3. Test endpoints individually
4. Review security configuration
5. Contact support with specific error details 