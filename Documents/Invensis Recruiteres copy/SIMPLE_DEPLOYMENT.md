# 🚀 Simple Render Deployment Guide

## **Step 1: Set up MongoDB Atlas (Required)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (free tier)
4. Click "Connect" → "Connect your application"
5. Copy the connection string (it looks like: `mongodb+srv://username:password@cluster.mongodb.net/database`)

## **Step 2: Deploy to Render**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect to your GitHub repository
4. Configure exactly like this:

### **Basic Settings:**
- **Name**: `invensis-hiring-api`
- **Root Directory**: (leave empty)
- **Environment**: `Node`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Plan**: `Free`

### **Build & Deploy Settings:**
- **Build Command**: `cd server && npm install`
- **Start Command**: `cd server && npm start`

## **Step 3: Add Environment Variables**

Click "Environment" tab and add these **EXACTLY**:

```
NODE_ENV=production
PORT=10000
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/invensis-recruiters
JWT_SECRET=d01ae62c9039aed4ec33146ede1c4b5aacdf73138e146b38ba7754619bed51ec148d5ab3d8e971561161ba6522ee9de0a9c4e6f6fc0ddb81f8052db3491db0bc
EMAIL_USER=testhrdp23@gmail.com
EMAIL_PASS=ujvdblbhpkxopqii
FRONTEND_URL=https://hiring.invensis.com
CORS_ORIGIN=https://hiring.invensis.com,https://admin.invensis.com
```

**⚠️ IMPORTANT:** Replace the `MONGODB_URI` with your actual MongoDB Atlas connection string!

## **Step 4: Deploy**

1. Click "Deploy Web Service"
2. Wait for build to complete (usually 2-3 minutes)
3. Your service will be available at: `https://your-service-name.onrender.com`

## **Step 5: Test**

After deployment, test these URLs:
- `https://your-service-name.onrender.com/api/health`
- `https://your-service-name.onrender.com/`

## **Troubleshooting**

If deployment fails:
1. Check that all environment variables are set correctly
2. Make sure MongoDB Atlas connection string is valid
3. Check Render logs for specific errors

## **Next Steps**

Once this works, we can deploy the admin server and frontend applications.

---
**Need help?** Share the error message from Render logs and I'll help you fix it! 