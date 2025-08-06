# Manual Render Deployment Guide

## 🚀 Step-by-Step Deployment

### Step 1: Create New Web Service in Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect to your GitHub repository: `https://github.com/Mo-nish/invensis-hiring-portal`

### Step 2: Configure the Service

**Basic Settings:**
- **Name**: `invensis-hiring-api`
- **Root Directory**: (leave empty - don't set to server)
- **Environment**: `Node`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Plan**: `Free`

**Build & Deploy Settings:**
- **Build Command**: `cd server && npm install`
- **Start Command**: `cd server && npm start`

### Step 3: Add Environment Variables

Click "Environment" tab and add these variables:

```
NODE_ENV=production
PORT=10000
MONGODB_URI=your-mongodb-atlas-connection-string
JWT_SECRET=your-secure-jwt-secret
EMAIL_USER=your-gmail-address
EMAIL_PASS=your-gmail-app-password
FRONTEND_URL=https://hiring.invensis.com
CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for the build to complete
3. Check the logs for any errors

### Step 5: Test the Deployment

Once deployed, test these endpoints:

- **Health Check**: `https://your-service.onrender.com/api/health`
- **Root Endpoint**: `https://your-service.onrender.com/`

### Troubleshooting

**If you get "cd: server: No such file or directory":**
1. Check that the `server` directory exists in your repository
2. Make sure you're on the `main` branch
3. Try pushing the latest changes: `git push origin main`

**If you get "npm install" errors:**
1. Check that `server/package.json` exists
2. Verify all dependencies are listed in `package.json`

**If the service starts but API calls fail:**
1. Check environment variables are set correctly
2. Verify MongoDB connection string
3. Check CORS settings

### Alternative Approach

If the above doesn't work, try this alternative configuration:

**Root Directory**: `server`
**Build Command**: `npm install`
**Start Command**: `npm start`

This tells Render to work directly in the `server` directory.

### Success Indicators

✅ **Successful deployment shows:**
- Build completes without errors
- Service status shows "Live"
- Health check returns JSON response
- API endpoints respond correctly

### Next Steps After Deployment

1. **Deploy Admin Server**: Repeat the process for the admin server
2. **Configure Custom Domains**: Set up your custom domain in Render
3. **Update Frontend**: Point your frontend to the new API URLs
4. **Test Everything**: Verify all functionality works

## 🆘 Need Help?

If you're still having issues:
1. Check the Render logs for specific error messages
2. Verify your repository structure matches the expected layout
3. Ensure all environment variables are set correctly
4. Test the build locally first: `cd server && npm install && npm start` 