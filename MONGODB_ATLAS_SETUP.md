# 🗄️ MongoDB Atlas Setup for Production

## 📋 Overview
Complete guide to set up MongoDB Atlas for your Invensis Hiring Portal production deployment.

---

## 🚀 **Step-by-Step MongoDB Atlas Setup**

### 1. **Create MongoDB Atlas Account**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Try Free"** or **"Sign Up"**
3. Create account with email/password or Google/GitHub

### 2. **Create New Cluster**
1. Click **"Build a Database"**
2. Choose **"M0 Sandbox"** (Free tier)
3. Select **Cloud Provider**: AWS, Google Cloud, or Azure
4. Choose **Region** closest to your users
5. Click **"Create Cluster"**

### 3. **Configure Database Access**
1. Go to **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Create username: `invensis-admin`
5. Generate secure password (save it!)
6. Set **Database User Privileges**: **"Read and write to any database"**
7. Click **"Add User"**

### 4. **Configure Network Access**
1. Go to **"Network Access"** in left sidebar
2. Click **"Add IP Address"**
3. For production: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
4. For security: Add specific IP addresses
5. Click **"Confirm"**

### 5. **Get Connection String**
1. Go to **"Database"** in left sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Select **"Python"** and **"Version 3.6 or later"**
5. Copy the connection string

### 6. **Update Connection String**
Replace `<password>` with your database user password:
```
mongodb+srv://invensis-admin:<password>@cluster0.xxxxx.mongodb.net/invensis?retryWrites=true&w=majority
```

---

## 🔧 **Render Environment Variables**

Add these to your Render environment variables:

```env
MONGODB_URI=mongodb+srv://invensis-admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/invensis?retryWrites=true&w=majority
```

---

## 🗂️ **Database Collections**

Your application will automatically create these collections:

### **Users Collection**
- Stores user accounts (admin, HR, manager, cluster, recruiter)
- Fields: email, name, role, password_hash, created_at, is_active

### **Candidates Collection**
- Stores candidate information
- Fields: name, email, phone, skills, experience, resume_path, image_path, status

### **Assignments Collection**
- Tracks candidate assignments to managers
- Fields: candidate_id, manager_id, hr_id, assigned_at, status, feedback

### **Candidate Requests Collection**
- Manages recruiter requests for candidates
- Fields: recruiter_id, requirements, status, created_at

### **Activity Logs Collection**
- Records system activities
- Fields: user_id, action, timestamp, details

---

## 🔒 **Security Best Practices**

### **Database Security**
- ✅ Use strong passwords
- ✅ Enable IP whitelisting
- ✅ Regular password rotation
- ✅ Monitor access logs

### **Application Security**
- ✅ Environment variables for sensitive data
- ✅ No hardcoded credentials
- ✅ Regular security updates

---

## 📊 **Monitoring & Maintenance**

### **Atlas Monitoring**
- **Metrics**: CPU, Memory, Connections
- **Alerts**: Set up notifications for issues
- **Backups**: Automatic daily backups (M2+ clusters)

### **Performance Optimization**
- **Indexes**: Automatically created for common queries
- **Connection Pooling**: Handled by PyMongo
- **Query Optimization**: Monitor slow queries

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Connection Refused**
- Check IP whitelist
- Verify username/password
- Ensure cluster is running

#### **Authentication Failed**
- Verify database user exists
- Check password is correct
- Ensure user has proper privileges

#### **Network Timeout**
- Check network access settings
- Verify connection string format
- Test from different network

---

## 🔄 **Backup Strategy**

### **Automatic Backups**
- **M0**: No automatic backups (free tier)
- **M2+**: Daily automated backups
- **Point-in-time recovery** available

### **Manual Backups**
```bash
# Export data
mongodump --uri="your-connection-string" --db=invensis

# Import data
mongorestore --uri="your-connection-string" --db=invensis
```

---

## 📈 **Scaling Options**

### **Cluster Tiers**
- **M0**: Free (512MB storage)
- **M2**: $9/month (2GB storage)
- **M5**: $25/month (5GB storage)
- **M10+**: Custom pricing

### **When to Scale**
- High memory usage
- Slow query performance
- Connection limit reached
- Storage space running low

---

## ✅ **Production Checklist**

- [ ] MongoDB Atlas account created
- [ ] Cluster deployed and running
- [ ] Database user created with proper privileges
- [ ] Network access configured
- [ ] Connection string obtained
- [ ] Environment variables set in Render
- [ ] Application tested with Atlas
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented

---

## 🎯 **Next Steps**

1. **Deploy to Render** with MongoDB Atlas connection
2. **Test all features** with production database
3. **Monitor performance** and usage
4. **Set up alerts** for critical issues
5. **Plan scaling** as user base grows

---

**🎉 Your MongoDB Atlas is ready for production!**
