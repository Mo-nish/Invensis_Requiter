# 🚀 Invensis Hiring Portal - Production Deployment Guide

## 📋 Current Status
✅ **GitHub Repository**: https://github.com/Mo-nish/invensis-hiring-portal  
✅ **Local Development**: Running on ports 5001 (main), 5002 (admin), 3000 (client)  
✅ **All Servers**: Operational and healthy  

## 🎯 Next Steps Overview

### 1. **Immediate Actions (Today)**
- [ ] Set up production environment variables
- [ ] Deploy to Vercel (Frontend)
- [ ] Deploy to Render (Backend)
- [ ] Configure MongoDB Atlas
- [ ] Set up email service

### 2. **Repository Enhancement (This Week)**
- [ ] Add issue templates
- [ ] Set up GitHub Actions CI/CD
- [ ] Add security scanning
- [ ] Create user documentation

### 3. **Production Testing (Next Week)**
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] User acceptance testing

## 🌐 Deployment Options

### Option A: Vercel + Render (Recommended)
**Frontend**: Vercel (Free tier available)  
**Backend**: Render (Free tier available)  
**Database**: MongoDB Atlas (Free tier available)  

### Option B: Railway (Full Stack)
**Everything**: Railway (Free tier available)  

### Option C: AWS/VPS (Advanced)
**Custom**: Full control, higher cost  

## 📦 Quick Production Deploy

### Step 1: Environment Setup
```bash
# Create production environment files
cp env.production.example .env.production
cp admin-portal/admin-server/env.production.example admin-portal/admin-server/.env.production
```

### Step 2: Deploy Frontend to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy main client
cd client
vercel --prod

# Deploy admin client
cd ../admin-portal/admin-client
vercel --prod
```

### Step 3: Deploy Backend to Render
```bash
# Use the deploy-render.sh script
./deploy-render.sh
```

## 🔧 Environment Configuration

### Production Environment Variables
```env
# Main Server (.env.production)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/invensis-recruiters
JWT_SECRET=your-super-secure-jwt-secret
ADMIN_JWT_SECRET=your-super-secure-admin-jwt-secret
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
PORT=5001
FRONTEND_URL=https://hiring.invensis.com
ADMIN_URL=https://admin.invensis.com
NODE_ENV=production

# Admin Server (admin-portal/admin-server/.env.production)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/invensis-recruiters
ADMIN_JWT_SECRET=your-super-secure-admin-jwt-secret
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
ADMIN_PORT=5002
FRONTEND_URL=https://hiring.invensis.com
ADMIN_URL=https://admin.invensis.com
NODE_ENV=production
```

## 🗄️ Database Setup

### MongoDB Atlas Configuration
1. **Create Cluster**: Free tier M0
2. **Network Access**: Allow all IPs (0.0.0.0/0) for development
3. **Database Access**: Create user with read/write permissions
4. **Connection String**: Use the provided connection string

### Database Collections
- `users` - User accounts and authentication
- `candidates` - Candidate information
- `assignments` - Manager-candidate assignments
- `roleassignments` - Admin role assignments
- `admins` - Admin user accounts

## 📧 Email Service Setup

### Gmail SMTP Configuration
1. **Enable 2-Factor Authentication**
2. **Generate App Password**
3. **Use App Password** in EMAIL_PASS

### SendGrid Alternative
```env
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=your-sendgrid-api-key
```

## 🔒 Security Checklist

### Pre-Deployment
- [ ] Change all default passwords
- [ ] Use strong JWT secrets
- [ ] Configure CORS properly
- [ ] Set up HTTPS
- [ ] Enable rate limiting

### Post-Deployment
- [ ] Test authentication flows
- [ ] Verify role-based access
- [ ] Check email functionality
- [ ] Monitor error logs
- [ ] Set up alerts

## 📊 Monitoring & Analytics

### Recommended Tools
- **Error Tracking**: Sentry (free tier)
- **Performance**: Vercel Analytics
- **Uptime**: UptimeRobot (free tier)
- **Logs**: Render logs or external service

## 🧪 Testing Strategy

### Automated Testing
```bash
# Run tests
npm test

# E2E testing with Cypress
npm run cypress:open
```

### Manual Testing Checklist
- [ ] User registration flow
- [ ] Admin role assignment
- [ ] HR candidate management
- [ ] Manager feedback submission
- [ ] Board member dashboard
- [ ] Email notifications
- [ ] File uploads
- [ ] Real-time updates

## 📚 Documentation

### User Guides Needed
- [ ] Admin User Guide
- [ ] HR User Guide
- [ ] Manager User Guide
- [ ] Board Member User Guide
- [ ] System Administrator Guide

### Technical Documentation
- [ ] API Documentation
- [ ] Database Schema
- [ ] Deployment Procedures
- [ ] Troubleshooting Guide

## 🚀 Deployment Scripts

### Quick Deploy Script
```bash
#!/bin/bash
# deploy-production.sh

echo "🚀 Starting production deployment..."

# 1. Build frontend
cd client && npm run build
cd ../admin-portal/admin-client && npm run build

# 2. Deploy to Vercel
vercel --prod

# 3. Deploy backend to Render
./deploy-render.sh

echo "✅ Deployment completed!"
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: ./deploy-production.sh
```

## 📞 Support & Maintenance

### Regular Tasks
- [ ] Weekly security updates
- [ ] Monthly performance review
- [ ] Quarterly feature updates
- [ ] Annual security audit

### Emergency Procedures
- [ ] Database backup procedures
- [ ] Rollback procedures
- [ ] Incident response plan
- [ ] Contact escalation list

---

## 🎉 Success Metrics

### Technical Metrics
- [ ] 99.9% uptime
- [ ] < 2 second page load times
- [ ] Zero security vulnerabilities
- [ ] 100% test coverage

### Business Metrics
- [ ] User adoption rate
- [ ] Feature usage statistics
- [ ] Support ticket volume
- [ ] User satisfaction scores

---

**Ready to deploy?** Follow the steps above or use the automated deployment scripts provided in the repository. 