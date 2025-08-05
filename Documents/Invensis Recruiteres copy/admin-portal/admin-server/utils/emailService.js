const nodemailer = require('nodemailer');

// Create transporter
const createTransporter = () => {
  console.log('🔍 Email Service Debug:');
  console.log('EMAIL_USER:', process.env.EMAIL_USER ? 'SET' : 'NOT SET');
  console.log('EMAIL_PASS:', process.env.EMAIL_PASS ? 'SET' : 'NOT SET');
  
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
    throw new Error('Email credentials not configured');
  }
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
};

// Generate invitation token
const generateInvitationToken = (email, role) => {
  const jwt = require('jsonwebtoken');
  return jwt.sign(
    { 
      email: email.toLowerCase(), 
      role, 
      type: 'invitation' 
    },
    process.env.ADMIN_JWT_SECRET || 'admin-secret-key',
    { expiresIn: '24h' }
  );
};

// Get registration URL based on environment
const getRegistrationUrl = (token) => {
  const baseUrl = process.env.NODE_ENV === 'production' 
    ? 'https://hiring.invensis.com' 
    : 'http://localhost:5001';
  return `${baseUrl}/register?token=${token}`;
};

// Send role assignment email
const sendRoleAssignmentEmail = async (email, role) => {
  try {
    const transporter = createTransporter();
    
    const token = generateInvitationToken(email, role);
    const registrationLink = getRegistrationUrl(token);
    
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Invensis Hiring Portal Access Invitation',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #1976d2;">Invensis Hiring Portal Access Invitation</h2>
          <p>Hello,</p>
          <p>You have been added to Invensis Hiring Portal as a <strong>${role}</strong>.</p>
          <p>Click the link below to complete your registration and set your password:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="${registrationLink}" 
               style="background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
              Complete Registration
            </a>
          </div>
          <p><strong>Registration Link:</strong> <a href="${registrationLink}">${registrationLink}</a></p>
          <p><strong>Important Notes:</strong></p>
          <ul>
            <li>Use the same email address (${email}) for registration</li>
            <li>Password must be at least 8 characters with letters and numbers</li>
            <li>Your role (${role}) will be automatically assigned</li>
            <li>This invitation expires in 24 hours</li>
          </ul>
          <p>If you have any questions, please contact the admin team.</p>
          <br>
          <p>Best regards,<br>Invensis Hiring Portal Team</p>
        </div>
      `
    };

    const result = await transporter.sendMail(mailOptions);
    console.log(`✅ Role assignment email sent to ${email}`);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Email sending failed:', error);
    throw error;
  }
};

// Send admin registration confirmation
const sendAdminRegistrationEmail = async (email, name) => {
  try {
    const transporter = createTransporter();
    
    const adminUrl = process.env.NODE_ENV === 'production' 
      ? 'https://admin.invensis.com' 
      : 'http://localhost:3002';
    
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Admin Registration Confirmation',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #1976d2;">Admin Registration Successful</h2>
          <p>Hello ${name},</p>
          <p>Your admin account has been created successfully in the Invensis Hiring Portal.</p>
          <p>You can now:</p>
          <ul>
            <li>Manage user roles</li>
            <li>Send role assignment invitations</li>
            <li>View system analytics and statistics</li>
            <li>Monitor user registrations and activity</li>
          </ul>
          <p>Access your admin dashboard at: <a href="${adminUrl}">${adminUrl}</a></p>
          <p>Best regards,<br>Invensis Hiring Portal Team</p>
        </div>
      `
    };

    await transporter.sendMail(mailOptions);
    console.log(`✅ Admin registration email sent to ${email}`);
    return { success: true };
  } catch (error) {
    console.error('❌ Admin registration email failed:', error);
    throw error;
  }
};

// Verify email configuration
const verifyEmailConfig = async () => {
  try {
    const transporter = createTransporter();
    await transporter.verify();
    console.log('✅ Email configuration verified successfully');
    return true;
  } catch (error) {
    console.error('❌ Email configuration error:', error);
    return false;
  }
};

module.exports = {
  sendRoleAssignmentEmail,
  sendAdminRegistrationEmail,
  verifyEmailConfig,
  generateInvitationToken,
  getRegistrationUrl
}; 