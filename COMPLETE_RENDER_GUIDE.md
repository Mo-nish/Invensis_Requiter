# 🚀 Complete Render Deployment Guide

## 📋 Overview
Step-by-step guide to deploy your Invensis Hiring Portal to Render with MongoDB Atlas.

---

## 🎯 **Prerequisites**
- ✅ GitHub repository: `Mo-nish/Invensis_Requiter`
- ✅ MongoDB Atlas account
- ✅ Gmail account for email notifications
- ✅ Render account (free tier available)

---

## 🚀 **Step 1: Deploy to Render**

### **1.1 Create Render Account**
1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account**
4. Authorize Render to access your repositories

### **1.2 Create Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect repository: **`Mo-nish/Invensis_Requiter`**
3. Configure service:

#### **Basic Settings**
- **Name**: `invensis-hiring-portal`
- **Environment**: `Python 3`
- **Branch**: `main`
- **Root Directory**: `/` (leave empty)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run.py`

#### **Advanced Settings**
- **Instance Type**: `Starter` (Free)
- **Auto-Deploy**: `Yes`
- **Health Check Path**: `/` (optional)

---

## 🗄️ **Step 2: MongoDB Atlas Setup**

### **2.1 Create MongoDB Atlas Account**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Try Free"**
3. Create account and verify email

### **2.2 Create Cluster**
1. Click **"Build a Database"**
2. Choose **"M0 Sandbox"** (Free tier)
3. Select **AWS** as provider
4. Choose **US East (N. Virginia)** region
5. Click **"Create Cluster"**

### **2.3 Configure Database Access**
1. Go to **"Database Access"**
2. Click **"Add New Database User"**
3. Username: `invensis-admin`
4. Password: Generate secure password
5. Privileges: **"Read and write to any database"**
6. Click **"Add User"**

### **2.4 Configure Network Access**
1. Go to **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Click **"Confirm"**

### **2.5 Get Connection String**
1. Go to **"Database"**
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Select **"Python"** and **"Version 3.6 or later"**
5. Copy connection string

---

## 🔧 **Step 3: Configure Environment Variables**

In Render dashboard, go to **Environment** tab and add:

### **Required Variables**
```env
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
MONGODB_URI=mongodb+srv://invensis-admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/invensis?retryWrites=true&w=majority
DEFAULT_ADMIN_EMAIL=admin@invensis.com
DEFAULT_ADMIN_PASSWORD=InvensisAdmin2025!
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
BASE_URL=https://invensis-hiring-portal.onrender.com
FLASK_ENV=production
```

### **Optional Variables**
```env
DEFAULT_ADMIN_NAME=Invensis Admin
PYTHON_VERSION=3.11.0
```

---

## 📧 **Step 4: Email Configuration**

### **4.1 Gmail Setup**
1. Enable **2-Factor Authentication** on Gmail
2. Go to **Google Account Settings**
3. **Security** → **2-Step Verification** → **App passwords**
4. Generate app password for "Mail"
5. Use this password in `EMAIL_PASS` variable

### **4.2 Test Email**
After deployment, test email functionality:
- User registration
- Password reset
- Role assignments
- Candidate notifications

---

## 🚀 **Step 5: Deploy and Test**

### **5.1 Deploy**
1. Click **"Create Web Service"** in Render
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors
4. Verify deployment URL

### **5.2 Test Application**
1. Visit your Render URL: `https://invensis-hiring-portal.onrender.com`
2. Test admin login:
   - **URL**: `https://invensis-hiring-portal.onrender.com/admin/login`
   - **Email**: `admin@invensis.com`
   - **Password**: `InvensisAdmin2025!`

### **5.3 Verify Features**
- ✅ Admin dashboard loads
- ✅ User management works
- ✅ Database connection active
- ✅ Email notifications work
- ✅ File uploads function
- ✅ All portals accessible

---

## 🔗 **Step 6: Access URLs**

After successful deployment, your application will be available at:

### **Main URLs**
- **Main Portal**: `https://invensis-hiring-portal.onrender.com`
- **Admin Portal**: `https://invensis-hiring-portal.onrender.com/admin/login`
- **HR Portal**: `https://invensis-hiring-portal.onrender.com/login`
- **Manager Portal**: `https://invensis-hiring-portal.onrender.com/login`
- **Cluster Portal**: `https://invensis-hiring-portal.onrender.com/login`
- **Recruiter Portal**: `https://invensis-hiring-portal.onrender.com/login`

### **Login Credentials**
- **Admin**: `admin@invensis.com` / `InvensisAdmin2025!`
- **HR**: `p.monishreddy19@gmail.com` / `Monish@007`

---

## 🔍 **Step 7: Monitoring & Maintenance**

### **7.1 Render Dashboard**
- **Logs**: Monitor application logs
- **Metrics**: CPU, Memory, Response time
- **Deployments**: Track deployment history
- **Environment**: Manage environment variables

### **7.2 MongoDB Atlas**
- **Metrics**: Database performance
- **Alerts**: Set up notifications
- **Backups**: Monitor backup status
- **Security**: Review access logs

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Build Failures**
- Check `requirements.txt` syntax
- Verify Python version compatibility
- Review build logs for errors

#### **Database Connection Issues**
- Verify MongoDB URI format
- Check network access settings
- Ensure database user exists

#### **Email Issues**
- Verify Gmail app password
- Check email configuration
- Test SMTP settings

#### **Application Errors**
- Check environment variables
- Review application logs
- Verify file permissions

---

## 📈 **Scaling & Optimization**

### **Render Scaling**
- **Starter**: Free tier (limited resources)
- **Standard**: $7/month (more resources)
- **Pro**: $25/month (production ready)

### **MongoDB Scaling**
- **M0**: Free (512MB storage)
- **M2**: $9/month (2GB storage)
- **M5**: $25/month (5GB storage)

---

## ✅ **Deployment Checklist**

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service configured
- [ ] MongoDB Atlas cluster created
- [ ] Database user configured
- [ ] Network access allowed
- [ ] Environment variables set
- [ ] Gmail app password generated
- [ ] Application deployed successfully
- [ ] All features tested
- [ ] Monitoring configured
- [ ] Backup strategy implemented

---

## 🎉 **Success!**

Your Invensis Hiring Portal is now live and ready for real users!

### **Production URL**
**`https://invensis-hiring-portal.onrender.com`**

### **Next Steps**
1. **Share URLs** with your team
2. **Create user accounts** for HR, managers, etc.
3. **Configure company branding**
4. **Set up monitoring alerts**
5. **Plan for scaling** as usage grows

---

**🚀 Your hiring portal is production-ready!**
