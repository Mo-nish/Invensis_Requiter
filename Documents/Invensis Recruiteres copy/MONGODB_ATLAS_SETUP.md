# 🗄️ MongoDB Atlas Setup Guide

## 📋 Prerequisites
- MongoDB Atlas account
- Access to MongoDB Atlas dashboard

## 🚀 Step-by-Step Setup

### 1. **Create/Verify MongoDB Atlas Cluster**

1. **Login to MongoDB Atlas**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Sign in with your account

2. **Check Your Cluster**
   - Verify cluster `cluster0.7m6bwkx.mongodb.net` exists
   - Ensure it's running (green status)

### 2. **Database Access Setup**

1. **Navigate to Database Access**
   - Go to Security → Database Access
   - Click "Add New Database User"

2. **Create Database User**
   ```
   Username: pmonishreddy19
   Password: [Create a new secure password]
   Database User Privileges: Atlas admin
   ```

3. **Password Requirements**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, and symbols
   - Avoid special characters that need URL encoding

### 3. **Network Access Setup**

1. **Navigate to Network Access**
   - Go to Security → Network Access
   - Click "Add IP Address"

2. **Add IP Address**
   - **Option A**: Add your current IP
   - **Option B**: Allow all IPs (for development): `0.0.0.0/0`

### 4. **Get Connection String**

1. **Go to Clusters**
   - Click on your cluster
   - Click "Connect"

2. **Choose Connection Method**
   - Select "Connect your application"
   - Choose "Node.js" as driver

3. **Copy Connection String**
   ```
   mongodb+srv://pmonishreddy19:<password>@cluster0.7m6bwkx.mongodb.net/?retryWrites=true&w=majority
   ```

### 5. **Test Connection**

1. **Update the test script with your new password**
   ```bash
   nano test-mongodb-connection.js
   ```

2. **Run the test**
   ```bash
   node test-mongodb-connection.js
   ```

## 🔧 Troubleshooting

### **Authentication Failed**
- ✅ Verify username is correct
- ✅ Reset database user password
- ✅ Check password doesn't contain problematic characters
- ✅ Ensure user has proper permissions

### **Connection Timeout**
- ✅ Add your IP to Network Access
- ✅ Use `0.0.0.0/0` for development
- ✅ Check cluster is running

### **Permission Denied**
- ✅ Ensure user has "Atlas admin" or "Read and write to any database"
- ✅ Check if database exists

## 📝 Quick Setup Commands

```bash
# 1. Test current connection
node test-mongodb-connection.js

# 2. Run comprehensive verification
node verify-mongodb-setup.js

# 3. Update environment files (after getting working password)
./setup-production-env.sh
```

## 🎯 Next Steps After Setup

1. **Update Environment Files**
   ```bash
   # Update with working password
   sed -i '' 's/your-password-here/working-password/g' .env.production
   sed -i '' 's/your-password-here/working-password/g' admin-portal/admin-server/.env.production
   ```

2. **Test Production Environment**
   ```bash
   # Test with production environment
   NODE_ENV=production node test-mongodb-connection.js
   ```

3. **Deploy to Production**
   ```bash
   ./deploy-production.sh
   ```

## 📞 Need Help?

If you're still having issues:

1. **Check MongoDB Atlas Status**: [Status Page](https://status.mongodb.com/)
2. **MongoDB Atlas Documentation**: [Docs](https://docs.atlas.mongodb.com/)
3. **Common Issues**: [Troubleshooting Guide](https://docs.atlas.mongodb.com/troubleshoot-connection/)

## 🔐 Security Best Practices

- ✅ Use strong passwords
- ✅ Limit IP access to necessary addresses
- ✅ Regularly rotate database passwords
- ✅ Use environment variables for sensitive data
- ✅ Enable MongoDB Atlas security features 