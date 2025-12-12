from flask import current_app
from flask_mail import Message
from threading import Thread
import os

def send_async_email(app, msg):
    try:
        with app.app_context():
            from app_mongo import mail
            mail.send(msg)
            print(f"✅ Email successfully sent to: {msg.recipients}")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print(f"❌ Email details - To: {msg.recipients}, Subject: {msg.subject}")
        import traceback
        traceback.print_exc()

def send_email(subject, recipients, body):
    try:
        app = current_app._get_current_object()
        msg = Message(subject, recipients=recipients)
        msg.body = body
        
        # Check if email is properly configured
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        
        if not mail_username or not mail_password:
            print(f"❌ EMAIL NOT CONFIGURED")
            print(f"   MAIL_USERNAME: {mail_username if mail_username else 'NOT_SET'}")
            print(f"   MAIL_PASSWORD: {'SET' if mail_password else 'NOT_SET'}")
            print(f"   EMAIL_USER env: {os.getenv('EMAIL_USER', 'NOT_SET')}")
            print(f"   EMAIL_PASS env: {'SET' if os.getenv('EMAIL_PASS') else 'NOT_SET'}")
            return False
        
        print(f"📧 Email configuration check:")
        print(f"   MAIL_USERNAME: {mail_username}")
        print(f"   MAIL_PASSWORD: {'SET' if mail_password else 'NOT_SET'}")
        print(f"   Recipients: {recipients}")
        print(f"   Subject: {subject}")
            
        Thread(target=send_async_email, args=(app, msg)).start()
        print(f"✅ Email queued for sending to: {recipients}")
        return True
    except Exception as e:
        print(f"❌ Error in send_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_role_assignment_email(email, role_type):
    """Send email notification when admin assigns a role"""
    subject = f"You've been designated as {role_type.title()}"
    
    body = f"""Hi there,

You've been designated as {role_type.title()} in the Invensis Hiring Portal.

Please register using your Gmail to access your dashboard.

Registration link: {os.getenv('BASE_URL', 'http://localhost:5000')}/register

Regards,
Admin Team
Invensis Hiring Portal
"""
    
    result = send_email(subject, [email], body)
    if not result:
        print(f"❌ Failed to send role assignment email to {email}")
    return result

def send_candidate_assignment_email(manager_email, candidate, interview_datetime):
    """Send email notification when HR assigns a candidate to manager"""
    subject = "New Candidate Assigned"
    
    # Format interview date and time
    interview_info = "TBD"
    if interview_datetime:
        interview_info = interview_datetime.strftime('%d %b %Y - %I:%M %p')
    
    body = f"""Dear Manager,

A new candidate has been assigned to you.

📅 Interview Date: {interview_info}
👤 Name: {candidate.first_name} {candidate.last_name}
🧠 Experience: {candidate.experience} Years
📍 Email: {candidate.email}
📞 Phone: {candidate.phone}
🆔 Reference ID: {candidate.reference_id}

Please review and proceed with the interview.

Dashboard: {os.getenv('BASE_URL', 'http://localhost:5001')}/manager/dashboard

Regards,
HR Team
Invensis Hiring Portal
"""
    
    result = send_email(subject, [manager_email], body)
    if not result:
        print(f"❌ Failed to send candidate assignment email to {manager_email}")
    return result

def send_feedback_notification_email(hr_email, candidate, status):
    """Send email notification when manager provides feedback"""
    subject = f"Feedback received for {candidate.name} ({candidate.reference_id})"
    
    body = f"""Hi HR,

Feedback has been received for candidate {candidate.name}.

Candidate Details:
- Name: {candidate.name}
- Reference ID: {candidate.reference_id}
- Status: {status.title()}
- Feedback: {candidate.feedback}

Please login to your dashboard to view the complete feedback.

Dashboard: {os.getenv('BASE_URL', 'http://localhost:5000')}/hr/dashboard

Regards,
Manager Team
Invensis Hiring Portal
"""
    
    send_email(subject, [hr_email], body)

def send_interview_scheduled_email(candidate_email, candidate, scheduled_date):
    """Send email notification when interview is scheduled"""
    subject = f"Interview scheduled: {candidate.reference_id}"
    
    body = f"""Hi {candidate.name},

Your interview has been scheduled.

Interview Details:
- Date: {scheduled_date.strftime('%Y-%m-%d')}
- Time: {scheduled_date.strftime('%H:%M')}
- Reference ID: {candidate.reference_id}

Please ensure you are available at the scheduled time.

Regards,
HR Team
Invensis Hiring Portal
"""
    
    send_email(subject, [candidate_email], body)

def send_invitation_email(email, role, registration_link):
    """Send invitation email for new user registration"""
    subject = f"Invensis Hiring Portal Access Invitation - {role}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">🚀 Invensis Hiring Portal</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Access Invitation</p>
        </div>
        
        <div style="background: white; padding: 30px; border: 1px solid #e1e5e9; border-radius: 0 0 10px 10px;">
            <h2 style="color: #2d3748; margin-top: 0;">Welcome to the Team!</h2>
            
            <p style="color: #4a5568; line-height: 1.6; font-size: 16px;">
                Hello there! 👋
            </p>
            
            <p style="color: #4a5568; line-height: 1.6; font-size: 16px;">
                You have been <strong>invited to join</strong> the <strong>Invensis Hiring Portal</strong> as a <strong style="color: #667eea;">{role}</strong>.
            </p>
            
            <div style="background: #f7fafc; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 0 5px 5px 0;">
                <h3 style="color: #2d3748; margin-top: 0;">🎯 Your Role</h3>
                <p style="color: #4a5568; margin: 0; font-size: 18px; font-weight: bold;">{role}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{registration_link}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                    🚀 Complete Registration
                </a>
            </div>
            
            <div style="background: #fff5f5; border: 1px solid #fed7d7; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h4 style="color: #c53030; margin-top: 0;">📋 Important Registration Details</h4>
                <ul style="color: #4a5568; line-height: 1.8;">
                    <li><strong>Email:</strong> Use <code style="background: #edf2f7; padding: 2px 6px; border-radius: 3px;">{email}</code> for registration</li>
                    <li><strong>Password:</strong> Minimum 8 characters with letters and numbers</li>
                    <li><strong>Role:</strong> Your role ({role}) will be automatically assigned</li>
                    <li><strong>Expiry:</strong> This invitation expires in 24 hours</li>
                </ul>
            </div>
            
            <div style="background: #f0fff4; border: 1px solid #9ae6b4; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h4 style="color: #22543d; margin-top: 0;">🔗 Alternative Registration Link</h4>
                <p style="color: #4a5568; margin: 0; word-break: break-all;">
                    If the button above doesn't work, copy and paste this link:<br>
                    <a href="{registration_link}" style="color: #667eea;">{registration_link}</a>
                </p>
            </div>
            
            <p style="color: #4a5568; line-height: 1.6; font-size: 16px;">
                If you have any questions or need assistance, please contact the admin team.
            </p>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e5e9;">
                <p style="color: #718096; margin: 0; font-size: 14px;">
                    Best regards,<br>
                    <strong>Invensis Hiring Portal Team</strong>
                </p>
            </div>
        </div>
    </div>
    """
    
    # Send HTML email
    from flask_mail import Message
    from app_mongo import mail
    
    msg = Message(
        subject=subject,
        recipients=[email],
        html=html_content
    )
    
    # Send email asynchronously
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()
    
    print(f"Invitation email sent to {email} for role: {role}") 

def send_password_reset_email(user_email, user_name, reset_token, base_url):
    """Send password reset email with secure token - synchronous for error reporting"""
    subject = "Password Reset Request - Invensis Hiring Portal"
    
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    
    body = f"""Hi {user_name},

You recently requested to reset your password for your Invensis Hiring Portal account.

🔐 **Reset Your Password**
Click the link below to reset your password:
{reset_url}

⚠️ **Important Security Notes:**
• This link will expire in 1 hour
• This link can only be used once
• If you didn't request this, please ignore this email
• For security, your current password will remain unchanged

🔒 **Password Requirements:**
• Minimum 8 characters
• Include uppercase and lowercase letters
• Include at least one number
• Include at least one special character

If you have any questions, please contact the admin team.

Regards,
Invensis Hiring Portal Team

---
This is an automated message. Please do not reply to this email.
"""
    
    try:
        from flask import current_app
        from flask_mail import Message
        from app_mongo import mail
        
        app = current_app._get_current_object()
        
        # Check if email is properly configured
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        
        if not mail_username or not mail_password:
            print(f"❌ EMAIL NOT CONFIGURED for password reset")
            print(f"   MAIL_USERNAME: {mail_username if mail_username else 'NOT_SET'}")
            print(f"   MAIL_PASSWORD: {'SET' if mail_password else 'NOT_SET'}")
            return False
        
        # Create message
        msg = Message(subject, recipients=[user_email], body=body)
        
        # Send email synchronously to catch errors
        with app.app_context():
            mail.send(msg)
            print(f"✅ Password reset email successfully sent to: {user_email}")
            return True
            
    except Exception as e:
        print(f"❌ Error sending password reset email to {user_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_password_changed_confirmation_email(user_email, user_name, base_url):
    """Send confirmation email when password is successfully changed"""
    subject = "Password Successfully Changed - Invensis Hiring Portal"
    
    login_url = f"{base_url}/login"
    
    body = f"""Hi {user_name},

Your password has been successfully changed for your Invensis Hiring Portal account.

✅ **Password Change Confirmed**
Your new password is now active and you can log in with it.

🔐 **Next Steps:**
• Visit the login page: {login_url}
• Sign in with your new password
• For security, you've been logged out of all active sessions

⚠️ **Security Alert:**
If you didn't make this change, please contact the admin team immediately.

Regards,
Invensis Hiring Portal Team

---
This is an automated message. Please do not reply to this email.
"""
    
    send_email(subject, [user_email], body) 