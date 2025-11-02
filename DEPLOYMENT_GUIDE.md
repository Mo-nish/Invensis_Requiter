# 🚀 Invensis Hiring Portal - Deployment Guide

## 📋 Overview
Complete hiring management system with AI-powered chatbot, role-based access control, and modern UI.

## 🌐 Repository
**GitHub:** https://github.com/Mo-nish/Invensis_Requiter

## 🔧 Quick Setup for Production

### 1. Clone Repository
```bash
git clone https://github.com/Mo-nish/Invensis_Requiter.git
cd Invensis_Requiter
```

### 2. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/invensis
DEFAULT_ADMIN_EMAIL=admin@yourcompany.com
DEFAULT_ADMIN_PASSWORD=YourSecurePassword123
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
BASE_URL=http://localhost:5001
```

### 4. Start Application
```bash
python run.py
```

## 🔑 Default Login Credentials

### Admin Portal
- **URL:** http://localhost:5001/admin/login
- **Email:** `invensisprocess@gmail.com`
- **Password:** `Monish@007`

### HR Portal
- **URL:** http://localhost:5001/login
- **Email:** `p.monishreddy19@gmail.com`
- **Password:** `Monish@007`

## 🎯 Features Ready for Production

### ✅ Admin Portal
- Role management (HR, Manager, Cluster, Recruiter)
- User assignment with email notifications
- Activity logging and monitoring
- System analytics

### ✅ HR Portal
- Candidate management with file uploads
- Manager assignment system
- Email notifications
- Candidate tracking and status updates

### ✅ Manager Portal
- Assigned candidate review
- Feedback submission system
- Status updates (shortlisted/rejected/on hold)
- Report export (CSV/PDF)
- Candidate reassignment

### ✅ Cluster Portal
- Strategic dashboard with analytics
- Performance metrics and insights
- HR submission summaries
- Manager performance tracking

### ✅ Recruiter Portal
- Candidate request management
- Request statistics and analytics
- Email notifications
- Status tracking

### ✅ AI Chatbot Widget
- Proactive suggestions
- Meeting reminders
- Real-time assistance
- Context-aware responses

## 🔒 Security Features
- Role-based access control
- Password hashing
- Session management
- Email verification
- JWT token authentication
- CSRF protection

## 📊 Database
- **MongoDB** integration
- User management
- Candidate tracking
- Assignment management
- Activity logging

## 🌐 Production Deployment Options

### Option 1: VPS/Cloud Server
1. Set up Ubuntu/CentOS server
2. Install Python 3.8+, MongoDB, Nginx
3. Clone repository and configure
4. Set up SSL certificate
5. Configure domain and DNS

### Option 2: Heroku
1. Create Heroku app
2. Add MongoDB Atlas addon
3. Set environment variables
4. Deploy from GitHub

### Option 3: DigitalOcean App Platform
1. Connect GitHub repository
2. Configure environment variables
3. Set up MongoDB database
4. Deploy automatically

## 📧 Email Configuration
1. Enable 2FA on Gmail
2. Generate App Password
3. Update `.env` with credentials
4. Test email functionality

## 🔧 Customization
- Update company branding in templates
- Modify email templates
- Configure chatbot responses
- Customize dashboard themes

## 📱 Mobile Responsive
- Works on all devices
- Touch-friendly interface
- Optimized for tablets and phones

## 🚀 Ready for Real Users!
The application is production-ready with:
- ✅ All features implemented and tested
- ✅ Security measures in place
- ✅ Modern UI/UX design
- ✅ Comprehensive documentation
- ✅ Error handling and logging
- ✅ Performance optimizations

## 📞 Support
For deployment assistance or customization, contact the development team.

---
**Status:** ✅ Production Ready
**Last Updated:** September 2025
**Version:** 1.0.0
