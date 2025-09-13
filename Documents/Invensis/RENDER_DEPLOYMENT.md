# 🚀 Render Deployment Guide - Invensis Hiring Portal

## 📋 Overview
Complete guide to deploy your Invensis Hiring Portal on Render platform.

## 🔗 Repository
**GitHub:** https://github.com/Mo-nish/Invensis_Requiter

---

## 🚀 **Step-by-Step Deployment**

### 1. **Create Render Account**
- Go to [render.com](https://render.com)
- Sign up with your GitHub account
- Connect your GitHub repository

### 2. **Deploy Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `Mo-nish/Invensis_Requiter`
3. Configure the service:

#### **Basic Settings**
- **Name:** `invensis-hiring-portal`
- **Environment:** `Python 3`
- **Branch:** `main`
- **Root Directory:** `/` (leave empty)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python run.py`

#### **Advanced Settings**
- **Instance Type:** `Starter` (Free tier)
- **Auto-Deploy:** `Yes` (deploys on git push)

### 3. **Set Environment Variables**
In Render dashboard, go to **Environment** tab and add:

```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/invensis
DEFAULT_ADMIN_EMAIL=admin@invensis.com
DEFAULT_ADMIN_PASSWORD=InvensisAdmin2025!
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
BASE_URL=https://your-app-name.onrender.com
```

### 4. **Set Up MongoDB Atlas**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free cluster
3. Create database user
4. Get connection string
5. Add to Render environment variables

### 5. **Deploy Database (Optional)**
If you want Render to manage MongoDB:
1. Click **"New +"** → **"PostgreSQL"** or **"MongoDB"**
2. Choose **"Starter"** plan
3. Connect to your web service

---

## 🔧 **Configuration Files**

### **render.yaml** (Already created)
```yaml
services:
  - type: web
    name: invensis-hiring-portal
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: MONGODB_URI
        fromDatabase:
          name: invensis-mongodb
          property: connectionString
```

### **Procfile** (Already created)
```
web: python run.py
```

---

## 🔑 **Production Login Credentials**

After deployment, you can access:

### **Admin Portal**
- **URL:** `https://your-app-name.onrender.com/admin/login`
- **Email:** `admin@invensis.com`
- **Password:** `InvensisAdmin2025!`

### **HR Portal**
- **URL:** `https://your-app-name.onrender.com/login`
- **Email:** `p.monishreddy19@gmail.com`
- **Password:** `Monish@007`

---

## 📧 **Email Setup**

### **Gmail Configuration**
1. Enable 2-Factor Authentication
2. Generate App Password
3. Update environment variables:
   - `EMAIL_USER=your-email@gmail.com`
   - `EMAIL_PASS=your-app-password`

---

## 🌐 **Custom Domain (Optional)**

1. In Render dashboard, go to **Settings**
2. Add your custom domain
3. Update DNS records
4. SSL certificate is automatically provided

---

## 🔍 **Monitoring & Logs**

- **Logs:** Available in Render dashboard
- **Metrics:** CPU, Memory, Response time
- **Health Checks:** Automatic monitoring

---

## 🚀 **Deployment Checklist**

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service configured
- [ ] Environment variables set
- [ ] MongoDB Atlas configured
- [ ] Email credentials updated
- [ ] Domain configured (optional)
- [ ] SSL certificate active
- [ ] Application deployed successfully

---

## 🎯 **Post-Deployment**

1. **Test Login:** Use admin credentials
2. **Create Users:** Add HR, Manager, Cluster users
3. **Configure Email:** Test email notifications
4. **Upload Files:** Test file upload functionality
5. **Monitor Performance:** Check logs and metrics

---

## 🔧 **Troubleshooting**

### **Common Issues**
- **Build Failures:** Check requirements.txt
- **Database Connection:** Verify MongoDB URI
- **Email Issues:** Check Gmail app password
- **Environment Variables:** Ensure all are set

### **Support**
- Render Documentation: [docs.render.com](https://docs.render.com)
- MongoDB Atlas: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)

---

## ✅ **Success!**

Your Invensis Hiring Portal will be live at:
**`https://your-app-name.onrender.com`**

🎉 **Ready for real users!**
