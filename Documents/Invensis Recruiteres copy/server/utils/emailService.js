const nodemailer = require('nodemailer');

// Check if email credentials are configured
const isEmailConfigured = process.env.EMAIL_USER && process.env.EMAIL_PASS;

// Log email configuration status
console.log('Email Configuration Status:');
console.log('- EMAIL_USER:', process.env.EMAIL_USER ? 'Configured' : 'Not configured');
console.log('- EMAIL_PASS:', process.env.EMAIL_PASS ? 'Configured' : 'Not configured');
console.log('- Email Service:', isEmailConfigured ? 'ENABLED' : 'DISABLED');

let transporter = null;

if (isEmailConfigured) {
  try {
    transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
      }
    });
    
    // Test the transporter configuration
    transporter.verify(function(error, success) {
      if (error) {
        console.error('❌ Email transporter verification failed:', error.message);
        console.log('📧 Email service will be disabled due to configuration issues');
        transporter = null;
      } else {
        console.log('✅ Email transporter verified successfully');
      }
    });
  } catch (error) {
    console.error('❌ Failed to create email transporter:', error.message);
    transporter = null;
  }
}

const sendAssignmentEmail = async (managerEmail, candidateName, referenceNumber, hrName, scheduleDate = null, managerName = null) => {
  console.log('📧 Attempting to send assignment email...');
  console.log('- To:', managerEmail);
  console.log('- Candidate:', candidateName);
  console.log('- Reference:', referenceNumber);
  console.log('- HR Name:', hrName);
  console.log('- Schedule Date:', scheduleDate);
  console.log('- Manager Name:', managerName);

  if (!transporter) {
    console.log('❌ Email service not configured. Skipping email notification.');
    console.log(`📋 Assignment notification: ${candidateName} (${referenceNumber}) assigned to ${managerEmail} by ${hrName}`);
    return { success: false, reason: 'Email service not configured' };
  }

  // Format schedule date if available
  const formattedScheduleDate = scheduleDate ? new Date(scheduleDate).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }) : 'Not scheduled yet';

  // Use manager name if provided, otherwise use a generic greeting
  const greeting = managerName ? `Hi ${managerName},` : 'Hi Manager,';

  const mailOptions = {
    from: process.env.EMAIL_USER,
    to: managerEmail,
    subject: 'New Candidate Assigned – Action Required',
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
          New Candidate Assignment
        </h2>
        
        <p style="font-size: 16px; color: #34495e;">
          ${greeting}
        </p>
        
        <p style="font-size: 16px; color: #34495e;">
          A new candidate has been assigned to you for interview scheduling and review.
        </p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3498db;">
          <h3 style="color: #2c3e50; margin-top: 0;">Candidate Details</h3>
          
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50; width: 150px;">Reference #:</td>
              <td style="padding: 8px 0; color: #34495e;">${referenceNumber}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Name:</td>
              <td style="padding: 8px 0; color: #34495e;">${candidateName}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Status:</td>
              <td style="padding: 8px 0; color: #34495e;">
                <span style="background-color: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                  New
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Scheduled Interview Date:</td>
              <td style="padding: 8px 0; color: #34495e;">${formattedScheduleDate}</td>
            </tr>
          </table>
        </div>
        
        <div style="background-color: #e8f4fd; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #3498db;">
          <p style="margin: 0; font-weight: bold; color: #2c3e50;">
            📋 Please log in to the Manager Dashboard to review and proceed.
          </p>
        </div>
        
        <p style="font-size: 16px; color: #34495e;">
          Regards,<br>
          <strong>Invensis Hiring Portal Team</strong>
        </p>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
          <p style="color: #7f8c8d; font-size: 12px;">
            This is an automated message from Invensis Hiring Portal System.
          </p>
        </div>
      </div>
    `
  };

  try {
    console.log('📤 Sending email...');
    const result = await transporter.sendMail(mailOptions);
    console.log('✅ Assignment email sent successfully to:', managerEmail);
    console.log('📧 Message ID:', result.messageId);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Error sending assignment email:', error);
    console.error('📧 Error details:', {
      code: error.code,
      command: error.command,
      response: error.response,
      responseCode: error.responseCode
    });
    return { success: false, error: error.message };
  }
};

const sendStatusUpdateEmail = async (hrEmail, candidateName, referenceNumber, status, managerName) => {
  console.log('📧 Attempting to send status update email...');
  console.log('- To:', hrEmail);
  console.log('- Candidate:', candidateName);
  console.log('- Reference:', referenceNumber);
  console.log('- Status:', status);
  console.log('- Manager Name:', managerName);

  if (!transporter) {
    console.log('❌ Email service not configured. Skipping email notification.');
    console.log(`📋 Status update notification: ${candidateName} (${referenceNumber}) status changed to ${status} by ${managerName}`);
    return { success: false, reason: 'Email service not configured' };
  }

  const mailOptions = {
    from: process.env.EMAIL_USER,
    to: hrEmail,
    subject: `Candidate Status Update - ${status}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
          Candidate Status Update
        </h2>
        
        <p style="font-size: 16px; color: #34495e;">
          Hi HR Team,
        </p>
        
        <p style="font-size: 16px; color: #34495e;">
          The status of a candidate has been updated:
        </p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3498db;">
          <h3 style="color: #2c3e50; margin-top: 0;">Update Details</h3>
          
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50; width: 150px;">Candidate Name:</td>
              <td style="padding: 8px 0; color: #34495e;">${candidateName}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Reference Number:</td>
              <td style="padding: 8px 0; color: #34495e;">${referenceNumber}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">New Status:</td>
              <td style="padding: 8px 0; color: #34495e;">
                <span style="background-color: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                  ${status}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Updated by:</td>
              <td style="padding: 8px 0; color: #34495e;">${managerName}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Date:</td>
              <td style="padding: 8px 0; color: #34495e;">${new Date().toLocaleDateString()}</td>
            </tr>
          </table>
        </div>
        
        <div style="background-color: #e8f4fd; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #3498db;">
          <p style="margin: 0; font-weight: bold; color: #2c3e50;">
            📋 Please log in to your Invensis Hiring Portal dashboard to view the complete details.
          </p>
        </div>
        
        <p style="font-size: 16px; color: #34495e;">
          Regards,<br>
          <strong>Invensis Hiring Portal Team</strong>
        </p>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
          <p style="color: #7f8c8d; font-size: 12px;">
            This is an automated message from Invensis Hiring Portal System.
          </p>
        </div>
      </div>
    `
  };

  try {
    console.log('📤 Sending status update email...');
    const result = await transporter.sendMail(mailOptions);
    console.log('✅ Status update email sent successfully to:', hrEmail);
    console.log('📧 Message ID:', result.messageId);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Error sending status update email:', error);
    console.error('📧 Error details:', {
      code: error.code,
      command: error.command,
      response: error.response,
      responseCode: error.responseCode
    });
    return { success: false, error: error.message };
  }
};

module.exports = { sendAssignmentEmail, sendStatusUpdateEmail }; 