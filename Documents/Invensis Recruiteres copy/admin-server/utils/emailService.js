const nodemailer = require('nodemailer');

// Create transporter
const createTransporter = () => {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
};

// Send role assignment notification
const sendRoleAssignmentEmail = async (email, role, adminName) => {
  try {
    const transporter = createTransporter();
    
    const registrationLink = `http://localhost:3000/register?email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`;
    
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: email,
      subject: `You have been designated as ${role}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #1976d2;">Role Assignment Notification</h2>
          <p>Hi,</p>
          <p>You have been designated as <strong>${role}</strong> in our Invensis Hiring Portal.</p>
          <p>Please register using your Gmail address to access your dashboard.</p>
          
          <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Registration Details:</h3>
            <p><strong>Email:</strong> ${email}</p>
            <p><strong>Role:</strong> ${role}</p>
            <p><strong>Registration Link:</strong> <a href="${registrationLink}" style="color: #1976d2;">Click here to register</a></p>
          </div>
          
          <p>Please use the same Gmail address (${email}) during registration.</p>
          <p>If you have any questions, please contact the admin team.</p>
          
          <p>Regards,<br>${adminName}<br>Admin Team</p>
        </div>
      `
    };

    const result = await transporter.sendMail(mailOptions);
    console.log('✅ Role assignment email sent:', result.messageId);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Role assignment email failed:', error);
    return { success: false, error: error.message };
  }
};

// Send admin registration confirmation
const sendAdminRegistrationEmail = async (email, adminName) => {
  try {
    const transporter = createTransporter();
    
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Admin Portal Access Confirmed',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #1976d2;">Admin Portal Access</h2>
          <p>Hi ${adminName},</p>
          <p>Your admin portal access has been successfully created.</p>
          <p>You can now log in to the admin portal at: <a href="http://localhost:3002" style="color: #1976d2;">http://localhost:3002</a></p>
          
          <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Admin Portal Features:</h3>
            <ul>
              <li>Manage HR user roles</li>
              <li>Manage Manager user roles</li>
              <li>Manage Board Member user roles</li>
              <li>View system analytics</li>
            </ul>
          </div>
          
          <p>Regards,<br>System Admin</p>
        </div>
      `
    };

    const result = await transporter.sendMail(mailOptions);
    console.log('✅ Admin registration email sent:', result.messageId);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Admin registration email failed:', error);
    return { success: false, error: error.message };
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
  verifyEmailConfig
}; 