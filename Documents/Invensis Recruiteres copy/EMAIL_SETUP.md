# Email Configuration Guide

## Overview
This guide helps you configure email notifications for the Invensis Hiring Portal.

## Email Service Status
The system uses Gmail SMTP for sending email notifications. Check the server logs for email configuration status:

```
Email Configuration Status:
- EMAIL_USER: Configured/Not configured
- EMAIL_PASS: Configured/Not configured  
- Email Service: ENABLED/DISABLED
```

## Setup Instructions

### 1. Gmail App Password Setup
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password:
   - Go to Security → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Invensis Hiring Portal"
   - Copy the generated 16-character password

### 2. Environment Configuration
Create or update your `.env` file in the root directory:

```env
# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-character-app-password
```

### 3. Testing Email Configuration
1. Start the server
2. Check server logs for email configuration status
3. Use the test email endpoint:
   ```bash
   curl -X POST http://localhost:5001/api/assignments/test-email \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"testEmail": "test@example.com"}'
   ```

## Troubleshooting

### Common Issues

#### 1. "Email service not configured"
**Solution**: Add EMAIL_USER and EMAIL_PASS to your .env file

#### 2. "Invalid login credentials"
**Solution**: 
- Use App Password, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled
- Check that the email address is correct

#### 3. "Less secure app access"
**Solution**: Use App Passwords instead of regular passwords

#### 4. "Connection timeout"
**Solution**:
- Check internet connection
- Verify firewall settings
- Try different network

### Debug Steps

1. **Check Configuration**:
   ```bash
   # Server logs will show:
   Email Configuration Status:
   - EMAIL_USER: Configured
   - EMAIL_PASS: Configured
   - Email Service: ENABLED
   ```

2. **Test Transporter**:
   ```bash
   # Server logs will show:
   ✅ Email transporter verified successfully
   ```

3. **Test Email Sending**:
   ```bash
   # Server logs will show:
   📧 Attempting to send assignment email...
   📤 Sending email...
   ✅ Assignment email sent successfully to: manager@example.com
   📧 Message ID: <message-id>
   ```

## Email Template
The system sends professional emails with:
- Subject: "New Candidate Assigned – Action Required"
- Candidate details (Reference #, Name, Status, Schedule Date)
- Call-to-action to log in to Manager Dashboard
- Professional formatting and branding

## Security Notes
- Never commit .env file to version control
- Use App Passwords, not regular passwords
- Regularly rotate App Passwords
- Monitor email sending logs for unusual activity

## Support
If you continue to have issues:
1. Check server logs for detailed error messages
2. Verify Gmail account settings
3. Test with a different Gmail account
4. Contact system administrator 