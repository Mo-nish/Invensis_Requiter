# 📧 Email Configuration Guide for Password Reset

## Problem
The forgot password feature shows "Email sent" but emails are not being received. This happens when the email service is not properly configured.

## Solution: Configure Gmail SMTP

### Step 1: Create Gmail App Password

1. **Go to your Google Account**: https://myaccount.google.com/
2. **Enable 2-Factor Authentication** (if not already enabled):
   - Go to Security → 2-Step Verification
   - Follow the setup process
3. **Generate App Password**:
   - Go to Security → App passwords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device
   - Enter "Invensis Hiring Portal"
   - Click "Generate"
   - **Copy the 16-character password** (you'll need this)

### Step 2: Set Environment Variables

#### For Local Development (.env file):
Create or update `.env` file in the root directory:

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-character-app-password
```

#### For Render (Production):
1. Go to your Render dashboard
2. Select your service
3. Go to "Environment" tab
4. Add these environment variables:
   - `EMAIL_USER` = your-email@gmail.com
   - `EMAIL_PASS` = your-16-character-app-password
5. Save and redeploy

### Step 3: Verify Configuration

After setting up, check the application logs. You should see:
```
Email config - USER: your-email@gmail.com
Email config - PASS: SET
Email config - SENDER: your-email@gmail.com
```

If you see `NOT_SET`, the environment variables are not configured correctly.

## Important Notes

⚠️ **Do NOT use your regular Gmail password!**
- You MUST use an App Password (16 characters)
- Regular passwords will NOT work with Gmail SMTP

⚠️ **Security:**
- App Passwords are safer than regular passwords
- You can revoke them anytime from Google Account settings
- Each app should have its own App Password

## Testing

1. Try the forgot password feature again
2. Check your email inbox (and spam folder)
3. If you see an error message, check the application logs for details

## Troubleshooting

### Error: "Email service is not configured"
- **Solution**: Make sure `EMAIL_USER` and `EMAIL_PASS` are set in environment variables

### Error: "Invalid login credentials"
- **Solution**: 
  - Use App Password, not regular password
  - Make sure 2-Factor Authentication is enabled
  - Verify the email address is correct

### Emails going to spam
- **Solution**: This is normal for automated emails. Check spam folder or mark as "Not Spam"

### Still not receiving emails
- Check application logs for error messages
- Verify SMTP settings in `app_mongo.py`:
  - Server: `smtp.gmail.com`
  - Port: `587`
  - TLS: `True`

## Current Status

After the latest update, the system will now:
- ✅ Check if email service is configured
- ✅ Show proper error message if email is not configured
- ✅ Only show "Email sent" when email is actually sent
- ✅ Log email sending status for debugging

