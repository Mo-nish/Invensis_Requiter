# 🗄️ MongoDB Atlas Setup Guide

## **Step 1: Create MongoDB Atlas Account**

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Click "Try Free" or "Get Started Free"
3. Fill in your details and create account

## **Step 2: Create a Cluster**

1. Click "Build a Database"
2. Choose "FREE" tier (M0)
3. Select your preferred cloud provider (AWS, Google Cloud, or Azure)
4. Choose a region close to you
5. Click "Create"

## **Step 3: Set Up Database Access**

1. In the left sidebar, click "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create a username and password (save these!)
5. Select "Read and write to any database"
6. Click "Add User"

## **Step 4: Set Up Network Access**

1. In the left sidebar, click "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for development)
4. Click "Confirm"

## **Step 5: Get Connection String**

1. Go back to "Database" in the left sidebar
2. Click "Connect"
3. Choose "Connect your application"
4. Copy the connection string

## **Step 6: Update Connection String**

Replace the connection string with your details:
```
mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/invensis-recruiters
```

**Replace:**
- `YOUR_USERNAME` with the username you created
- `YOUR_PASSWORD` with the password you created
- `cluster0.xxxxx.mongodb.net` with your actual cluster URL

## **Step 7: Test Connection**

You can test if your connection string works by trying to connect to your database.

---

**⚠️ Important Notes:**
- Keep your username and password secure
- The connection string will be used in Render environment variables
- Make sure to replace the placeholder values in the deployment guide 