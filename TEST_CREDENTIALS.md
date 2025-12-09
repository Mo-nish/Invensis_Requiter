# 🔑 Test Credentials for Invensis Hiring Portal

## 📋 Admin Credentials

### Primary Admin Account
- **Email**: `p.monishreddy19@gmail.com`
- **Password**: `Monish@007`
- **Role**: Admin
- **Login URL**: `http://localhost:5001/admin/login`

### Default Admin Account (if exists)
- **Email**: `admin@invensis.com`
- **Password**: `Monish@007` (default, check environment variable `DEFAULT_ADMIN_PASSWORD`)
- **Role**: Admin
- **Login URL**: `http://localhost:5001/admin/login`

---

## 🧪 Testing Different User Roles

### How to Create Test Users for Other Roles

The application uses a role-based system where:
1. **Admin** assigns roles to users via the admin dashboard
2. Users must be **pre-approved** (added to `UserEmail` collection) before they can register
3. Users register at `/register` and get assigned their pre-approved role

### Available Roles:
- **Admin** - Full system access
- **HR** - Add candidates, assign to managers
- **Manager** - Review candidates, provide feedback
- **Recruiter** - Similar to HR
- **Cluster** - Strategic overview and analytics

---

## 🚀 Quick Testing Steps

### 1. Test Admin Login
```
URL: http://localhost:5001/admin/login
Email: p.monishreddy19@gmail.com
Password: Monish@007
```

### 2. Create Test Users for Other Roles

**Option A: Via Admin Dashboard**
1. Login as admin
2. Navigate to user management
3. Assign roles to email addresses
4. Users will receive invitation emails
5. Users can then register at `/register`

**Option B: Direct Database Entry**
- Add entries to MongoDB `user_emails` collection with:
  - `email`: test email address
  - `role`: 'HR', 'Manager', 'Recruiter', or 'Cluster Member'
  - `is_active`: true

### 3. Test User Registration
```
URL: http://localhost:5001/register
- Use an email that has been pre-approved by admin
- Set a password (min 8 chars, uppercase, lowercase, number, special char)
```

---

## 🔍 Verify Users Exist

Run the verification script:
```bash
cd Documents/Invensis
python verify_admin.py
```

This will show:
- ✅ Which admin users exist
- ✅ Their roles and active status
- ✅ Login credentials

---

## 📝 Password Requirements

When creating new users or resetting passwords:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*(),.?":{}|<>)

---

## 🌐 Application URLs

- **Homepage**: `http://localhost:5001/`
- **Admin Login**: `http://localhost:5001/admin/login`
- **General Login**: `http://localhost:5001/login`
- **Registration**: `http://localhost:5001/register`
- **Forgot Password**: `http://localhost:5001/forgot-password`

---

## ⚠️ Important Notes

1. **Default Admin Password**: Can be changed via environment variable `DEFAULT_ADMIN_PASSWORD`
2. **Email Authorization**: Users must be pre-approved in the `user_emails` collection before registration
3. **Role Assignment**: Only admins can assign roles to users
4. **Password Reset**: Users can reset passwords via the forgot password flow

---

## 🧹 Testing Checklist

- [ ] Admin can login at `/admin/login`
- [ ] Admin can assign roles to users
- [ ] Pre-approved users can register at `/register`
- [ ] Users can login at `/login` with their credentials
- [ ] HR users can add candidates
- [ ] Managers can view assigned candidates
- [ ] Password reset flow works (`/forgot-password`)
- [ ] Role-based access control is enforced

---

**Last Updated**: Based on current codebase configuration
**Default Port**: 5001 (check your `run.py` or environment configuration)

