# 🚀 Complete Deployment Guide - Invensis Hiring Portal

## **📋 Current Status**
- **Hiring Server**: `https://invensis-hiring-server.onrender.com` - Starting up
- **Admin Server**: `https://invensis-admin-server.onrender.com` - Starting up

## **🔧 Issues Fixed**

### **1. Admin Server Configuration**
- ✅ Fixed PORT environment variable (was using ADMIN_PORT)
- ✅ Updated CORS configuration for production
- ✅ Added root endpoint for health checking
- ✅ Created separate Render configuration

### **2. Server Configurations**
- ✅ Both servers now use `PORT=10000` (Render default)
- ✅ Proper CORS configuration for production URLs
- ✅ Enhanced error handling and logging

## **🚀 Deployment Steps**

### **Step 1: Deploy Hiring Server**

1. **Go to Render Dashboard**
2. **Create New Web Service**
3. **Connect your GitHub repository**
4. **Configure:**
   - **Name**: `invensis-hiring-server`
   - **Root Directory**: `server`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`

5. **Environment Variables:**
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

### **Step 2: Deploy Admin Server**

1. **Create another Web Service**
2. **Configure:**
   - **Name**: `invensis-admin-server`
   - **Root Directory**: `admin-portal/admin-server`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`

3. **Environment Variables:**
   ```
   NODE_ENV=production
   PORT=10000
   MONGODB_URI=your-mongodb-atlas-connection-string
   ADMIN_JWT_SECRET=your-secure-admin-jwt-secret
   EMAIL_USER=your-gmail-address
   EMAIL_PASS=your-gmail-app-password
   FRONTEND_URL=https://admin.invensis.com
   CORS_ORIGIN=https://admin.invensis.com,https://hiring.invensis.com
   ```

## **🔍 Testing Deployment**

### **Hiring Server Endpoints:**
- **Health Check**: `https://invensis-hiring-server.onrender.com/api/health`
- **Root**: `https://invensis-hiring-server.onrender.com/`
- **Auth**: `https://invensis-hiring-server.onrender.com/api/auth/login`

### **Admin Server Endpoints:**
- **Health Check**: `https://invensis-admin-server.onrender.com/api/admin/health`
- **Root**: `https://invensis-admin-server.onrender.com/`
- **Admin Auth**: `https://invensis-admin-server.onrender.com/api/admin/auth/login`

## **🔑 Admin Login Credentials**
- **Email**: `admin@invensis.com`
- **Password**: `admin123`

## **📊 Expected Response Examples**

### **Hiring Server Health Check:**
```json
{
  "status": "OK",
  "message": "Invensis Hiring Portal API is running",
  "timestamp": "2025-08-06T07:47:49.110Z",
  "environment": "production"
}
```

### **Admin Server Health Check:**
```json
{
  "status": "OK",
  "message": "Admin server is running",
  "timestamp": "2025-08-06T07:47:49.202Z",
  "environment": "production"
}
```

## **🔧 Troubleshooting**

### **If servers show "WELCOME TO RENDER":**
1. Wait 2-3 minutes for full startup
2. Check Render logs for errors
3. Verify environment variables are set
4. Test health endpoints

### **If health checks fail:**
1. Check MongoDB connection
2. Verify JWT secrets are set
3. Check email configuration
4. Review server logs in Render dashboard

### **Common Issues:**
- **MongoDB Connection**: Ensure Atlas cluster is accessible
- **Email Service**: Verify Gmail app password is correct
- **CORS Errors**: Check CORS_ORIGIN configuration
- **Port Issues**: Both servers should use PORT=10000

## **🎯 Next Steps**

1. **Deploy both servers** using the configurations above
2. **Wait for startup** (2-3 minutes)
3. **Test health endpoints** to verify deployment
4. **Test admin login** with provided credentials
5. **Deploy frontend applications** (separate process)

## **📞 Support**

If deployment fails:
1. Check Render logs for specific errors
2. Verify all environment variables are set
3. Test MongoDB connection separately
4. Ensure all dependencies are installed

---
**Last Updated**: August 6, 2025
**Status**: ✅ Ready for Deployment 