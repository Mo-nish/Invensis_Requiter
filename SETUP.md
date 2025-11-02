# Invensis Hiring Portal - Setup Guide

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
BASE_URL=http://localhost:5000
```

### 3. Database Initialization
```bash
# Create admin user
python init_db.py
```

### 4. Start Application
```bash
# Run the application
python run.py
```

### 5. Access the Application
- **Main Portal**: http://localhost:5000
- **Admin Portal**: http://localhost:5000/admin/login

## 📋 Features Implemented

### ✅ Admin Portal (`/admin`)
- [x] Secure admin login
- [x] Role management (HR, Manager, Cluster)
- [x] Email assignment notifications
- [x] Activity logging
- [x] User access control

### ✅ HR Portal (`/hr`)
- [x] Candidate management
- [x] File upload (resume, image)
- [x] Manager assignment
- [x] Email notifications
- [x] Candidate tracking

### ✅ Manager Portal (`/manager`)
- [x] Assigned candidate review
- [x] Feedback submission
- [x] Status updates (shortlisted/rejected/on hold)
- [x] Report export (CSV/PDF)
- [x] Candidate reassignment

### ✅ Cluster Portal (`/cluster`)
- [x] Strategic dashboard
- [x] Analytics charts
- [x] Performance metrics
- [x] HR submission summaries
- [x] Manager insights

### ✅ Core Features
- [x] Role-based access control
- [x] Email notifications
- [x] File upload system
- [x] Modern UI with animations
- [x] Responsive design
- [x] Database management
- [x] Session handling
- [x] Security features

## 🎨 UI/UX Features

### Design Elements
- **Modern Interface**: Clean, professional design
- **Responsive Layout**: Works on all devices
- **Smooth Animations**: Fade-in, slide transitions
- **Interactive Charts**: Chart.js integration
- **Color-coded Status**: Visual status indicators
- **Hover Effects**: Enhanced user experience

### Navigation
- **Tab-based Interface**: Easy switching between sections
- **Breadcrumb Navigation**: Clear user location
- **Modal Dialogs**: Clean form interactions
- **Flash Messages**: User feedback system

## 🔧 Technical Implementation

### Backend Architecture
- **Flask Framework**: Python web framework
- **SQLAlchemy ORM**: Database management
- **Blueprint Structure**: Modular route organization
- **Session Management**: Secure user sessions
- **File Upload**: Secure document handling

### Database Schema
- **Users**: Authentication and role management
- **Roles**: Permission system
- **Candidates**: Recruitment data
- **Activity Logs**: System audit trail
- **Feedback**: Manager reviews

### Security Features
- **Password Hashing**: Secure credential storage
- **Role-based Access**: Permission control
- **Session Management**: Secure user sessions
- **Input Validation**: Data sanitization
- **File Upload Security**: Safe document handling

## 📧 Email System

### Notification Types
- **Role Assignment**: Admin assigns roles
- **Candidate Assignment**: HR assigns to managers
- **Feedback Alerts**: Manager provides feedback
- **Interview Scheduling**: Automated confirmations

### Configuration
- **Gmail SMTP**: Primary email service
- **App Passwords**: Secure authentication
- **Template System**: Professional email templates

## 📊 Analytics & Reporting

### Dashboard Features
- **Real-time Metrics**: Live data updates
- **Status Distribution**: Visual candidate status
- **Manager Performance**: Review metrics
- **HR Submissions**: Activity tracking

### Export Capabilities
- **CSV Export**: Data analysis
- **PDF Reports**: Professional documentation
- **Custom Filters**: Targeted reporting

## 🚀 Deployment Ready

### Production Considerations
- **Environment Variables**: Secure configuration
- **Database Migration**: Schema management
- **Static File Serving**: Optimized delivery
- **Error Handling**: Robust error management
- **Logging**: System monitoring

### Scalability Features
- **Modular Architecture**: Easy to extend
- **Blueprint Structure**: Organized codebase
- **Database Abstraction**: Easy to switch databases
- **Configuration Management**: Environment-specific settings

## 🔍 Testing

### Test Coverage
- **Import Tests**: Module verification
- **Database Tests**: Schema validation
- **Route Tests**: Endpoint verification
- **Template Tests**: UI component checks
- **Directory Tests**: File structure validation

### Quality Assurance
- **Code Organization**: Clean, maintainable code
- **Error Handling**: Graceful failure management
- **Security Validation**: Input sanitization
- **Performance Optimization**: Efficient queries

## 📝 Usage Workflow

### Admin Workflow
1. Login to admin portal
2. Assign roles to users
3. Monitor system activity
4. View activity logs

### HR Workflow
1. Add new candidates
2. Upload documents
3. Assign to managers
4. Track candidate status

### Manager Workflow
1. Review assigned candidates
2. Provide feedback
3. Update status
4. Export reports

### Cluster Workflow
1. View strategic dashboard
2. Analyze performance metrics
3. Monitor HR activity
4. Generate insights

## 🎯 Success Criteria Met

### ✅ Requirements Fulfilled
- [x] Centralized hiring tool
- [x] Role-based dashboards
- [x] Clean, modern design
- [x] Smooth animations
- [x] Email notifications
- [x] Admin portal consistency
- [x] Proper redirects
- [x] File upload system
- [x] Analytics dashboard
- [x] Export functionality

### ✅ Technical Excellence
- [x] Secure authentication
- [x] Database management
- [x] Error handling
- [x] Code organization
- [x] Documentation
- [x] Testing coverage

## 🚀 Next Steps

### Immediate Actions
1. **Set up email configuration**
2. **Create admin user**
3. **Test all portals**
4. **Configure production settings**

### Future Enhancements
- **Advanced analytics**
- **Mobile app integration**
- **API endpoints**
- **Third-party integrations**
- **Advanced reporting**

---

**Invensis Hiring Portal** - A comprehensive solution for streamlined recruitment management. 