# Invensis Hiring Portal

A comprehensive hiring management system with role-based access control, featuring HR, Manager, and Board Member dashboards with real-time candidate tracking and feedback systems.

## 🚀 Features

### Core Functionality
- **Role-Based Access Control**: HR, Manager, Board Member, and Admin roles
- **Admin-Controlled Registration**: Invitation-based user registration system
- **Real-Time Dashboard**: Live updates and auto-refresh functionality
- **Candidate Management**: Complete candidate lifecycle tracking
- **Feedback System**: HR and Manager feedback with ratings
- **Assignment Tracking**: Manager-candidate assignment system

### Dashboards
- **HR Dashboard**: Candidate creation, management, and HR feedback
- **Manager Dashboard**: Assigned candidates, feedback submission, review history
- **Clusters Dashboard**: Comprehensive overview for Board Members
- **Admin Portal**: User management, role assignments, system analytics

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **Email Notifications**: Automated invitation and notification system
- **File Upload**: Resume and profile image uploads
- **Real-Time Updates**: Auto-refresh and live data synchronization
- **Responsive Design**: Mobile-friendly Material-UI interface

## 🛠️ Tech Stack

### Backend
- **Node.js** with Express.js
- **MongoDB** with Mongoose ODM
- **JWT** for authentication
- **Nodemailer** for email services
- **bcryptjs** for password hashing

### Frontend
- **React.js** with hooks
- **Material-UI** for components
- **React Router** for navigation
- **Axios** for API calls
- **React Toastify** for notifications

### Development Tools
- **Nodemon** for server auto-restart
- **Concurrently** for running multiple processes
- **ESLint** for code quality

## 📋 Prerequisites

- Node.js (v14 or higher)
- MongoDB (local or Atlas)
- npm or yarn package manager

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd invensis-hiring-portal
   ```

2. **Install dependencies**
   ```bash
   npm run install-all
   ```

3. **Environment Setup**
   ```bash
   # Copy environment files
   cp env.example .env
   cp admin-portal/admin-server/env.example admin-portal/admin-server/.env
   ```

4. **Configure Environment Variables**
   
   **Main Server (.env):**
   ```env
   MONGODB_URI=mongodb://localhost:27017/invensis-recruiters
   JWT_SECRET=your-jwt-secret
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   PORT=5001
   ```

   **Admin Server (admin-portal/admin-server/.env):**
   ```env
   MONGODB_URI=mongodb://localhost:27017/invensis-recruiters
   ADMIN_JWT_SECRET=your-admin-jwt-secret
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   ADMIN_PORT=5002
   ```

5. **Start the application**
   ```bash
   npm run dev
   ```

## 🌐 Access URLs

- **Main Portal**: http://localhost:3000
- **Admin Portal**: http://localhost:3002
- **Main API**: http://localhost:5001
- **Admin API**: http://localhost:5002

## 👥 User Roles & Permissions

### Admin
- Manage user roles and permissions
- Send invitation emails
- View system analytics
- Monitor user activity

### HR
- Create and manage candidates
- Assign candidates to managers
- Provide HR feedback and ratings
- View candidate status

### Manager
- Review assigned candidates
- Submit feedback and ratings
- Schedule interviews
- Track candidate progress

### Board Member
- View comprehensive system overview
- Monitor HR and Manager feedback
- Access real-time statistics
- Review candidate timelines

## 📁 Project Structure

```
invensis-hiring-portal/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/      # Login/Register
│   │   │   ├── hr/        # HR Dashboard
│   │   │   ├── manager/   # Manager Dashboard
│   │   │   ├── board/     # Clusters Dashboard
│   │   │   └── common/    # Shared components
│   │   └── contexts/      # Auth context
├── server/                 # Main backend
│   ├── models/            # Database models
│   ├── routes/            # API routes
│   ├── middleware/        # Auth middleware
│   └── utils/             # Utility functions
├── admin-portal/          # Admin portal
│   ├── admin-client/      # Admin React frontend
│   └── admin-server/      # Admin backend
├── uploads/               # File uploads
└── docs/                  # Documentation
```

## 🔧 Available Scripts

```bash
# Development
npm run dev              # Start both frontend and backend
npm run server           # Start backend only
npm run client           # Start frontend only

# Production
npm start               # Start production server
npm run build           # Build frontend for production

# Installation
npm run install-all     # Install all dependencies
```

## 📧 Email Configuration

The system uses Gmail SMTP for sending invitation emails. Configure your email settings in the environment files:

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Add the credentials to your `.env` files

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- Admin-controlled user registration
- Secure file upload handling
- CORS configuration

## 🚀 Deployment

### Local Development
```bash
npm run dev
```

### Production Deployment
1. Set up environment variables for production
2. Build the frontend: `npm run build`
3. Start the server: `npm start`

### Cloud Deployment Options
- **Render**: Backend deployment
- **Vercel**: Frontend deployment
- **Railway**: Full-stack deployment
- **AWS EC2**: Custom server setup

## 📊 Database Schema

### Collections
- **Users**: User accounts and authentication
- **Candidates**: Candidate information and profiles
- **Assignments**: Manager-candidate assignments
- **RoleAssignments**: Admin-managed role assignments
- **Admins**: Admin user accounts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is proprietary software for Invensis Company.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

## 🔄 Version History

- **v1.0.0**: Initial release with basic functionality
- **v1.1.0**: Added Clusters Dashboard and real-time updates
- **v1.2.0**: Enhanced feedback system and UI improvements

---

**Built with ❤️ for Invensis Company** 