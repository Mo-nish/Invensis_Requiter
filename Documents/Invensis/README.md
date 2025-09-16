# Invensis Hiring Portal

A comprehensive centralized hiring tool that enables collaboration between Admin, HRs, Managers, and Cluster Leads with clean design, role-based dashboards, animations, and email notifications.

## 🚀 Features

### 🔐 Role-Based Access Control
- **Admin Portal** (`/admin`): Manage user roles and system access
- **HR Portal** (`/hr`): Add candidates and assign to managers
- **Manager Portal** (`/manager`): Review candidates and provide feedback
- **Cluster Portal** (`/cluster`): Strategic overview and analytics

### 📧 Email Notifications
- Automated role assignment emails
- Candidate assignment notifications
- Feedback submission alerts
- Interview scheduling confirmations

### 📊 Analytics & Reporting
- Real-time dashboard with charts
- Manager performance metrics
- HR submission summaries
- Export functionality (CSV/PDF)

### 🎨 Modern UI/UX
- Responsive design with Tailwind CSS
- Smooth animations and transitions
- Interactive charts with Chart.js
- Clean, professional interface

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **Email**: Gmail SMTP
- **File Upload**: Image and PDF support

## 📁 Project Structure

```
invensis-hiring-tool/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
├── templates/
│   ├── admin/
│   ├── hr/
│   ├── manager/
│   └── cluster/
├── routes/
│   ├── admin.py
│   ├── hr.py
│   ├── manager.py
│   └── cluster.py
├── app.py
├── models.py
├── email_service.py
├── requirements.txt
└── README.md
```

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd invensis-hiring-tool
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
BASE_URL=http://localhost:5000
```

### 5. Initialize Database
```bash
python app.py
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 👥 User Roles & Workflows

### 🔧 Admin
- **Access**: `/admin/login`
- **Features**:
  - Assign roles to users (HR, Manager, Cluster)
  - Monitor system activity
  - View activity logs
  - Send role assignment emails

### 👥 HR
- **Access**: `/login` (after admin approval)
- **Features**:
  - Add new candidates with documents
  - Assign candidates to managers
  - Track candidate status
  - Upload resumes and images

### 👔 Manager
- **Access**: `/login` (after admin approval)
- **Features**:
  - Review assigned candidates
  - Provide feedback and status updates
  - Export feedback reports
  - Reassign candidates to HR

### 📊 Cluster Lead
- **Access**: `/login` (after admin approval)
- **Features**:
  - Strategic overview dashboard
  - Analytics and performance metrics
  - Manager performance insights
  - HR submission summaries

## 📧 Email Configuration

### Gmail SMTP Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update the `.env` file with your credentials

### Email Templates
- Role assignment notifications
- Candidate assignment alerts
- Feedback submission confirmations
- Interview scheduling notifications

## 🔒 Security Features

- Role-based access control
- Session management
- Password hashing
- Email verification for registration
- Admin-only role assignments

## 📊 Database Schema

### Users
- Email, name, role, password_hash
- Created_at, is_active

### Roles
- Email, role_type, assigned_by
- Assigned_at, is_active

### Candidates
- Reference_id, name, email, phone
- Gender, age, education, experience
- Resume_path, image_path, status
- Assigned_to, assigned_by, scheduled_date
- Feedback, created_at, updated_at

### Activity Logs
- User_email, action, target_email
- Details, timestamp, ip_address

### Feedback
- Candidate_id, manager_email
- Feedback_text, status, created_at

## 🎨 UI Features

### Animations
- Fade-in effects on page load
- Slide transitions between tabs
- Hover effects on cards
- Button animations

### Responsive Design
- Mobile-friendly layouts
- Adaptive grid systems
- Touch-friendly interfaces

### Charts & Visualizations
- Status distribution pie charts
- Manager performance bar charts
- Real-time data updates

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set up a production server
2. Configure environment variables
3. Use a production WSGI server (Gunicorn)
4. Set up a reverse proxy (Nginx)
5. Configure SSL certificates

## 🔧 Configuration

### Database
- Default: SQLite (development)
- Production: PostgreSQL recommended

### Email
- Gmail SMTP (default)
- SendGrid (alternative)

### File Upload
- Supported formats: PNG, JPG, JPEG, GIF, PDF
- Maximum file size: Configure in app settings

## 📝 API Endpoints

### Admin Routes
- `POST /admin/add_role` - Assign new role
- `POST /admin/remove_role` - Remove role
- `GET /admin/activity_logs` - View activity logs

### HR Routes
- `POST /hr/add_candidate` - Add new candidate
- `POST /hr/assign_candidate` - Assign to manager
- `GET /hr/candidates` - View all candidates

### Manager Routes
- `POST /manager/add_feedback` - Add feedback
- `POST /manager/reassign_candidate` - Reassign to HR
- `GET /manager/export_feedback` - Export reports

### Cluster Routes
- `GET /cluster/analytics` - Detailed analytics
- `GET /cluster/reports` - Generate reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### v1.0.0
- Initial release
- Complete role-based system
- Email notifications
- Analytics dashboard
- Modern UI/UX

---

**Invensis Hiring Portal** - Streamlining recruitment management for seamless collaboration. # Deployment fix Tue Sep 16 09:20:00 IST 2025
