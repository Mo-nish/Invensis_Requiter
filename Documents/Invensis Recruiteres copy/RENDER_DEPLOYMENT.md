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
