#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('📧 Invensis Hiring Portal - Email Configuration Setup');
console.log('===================================================\n');

// Check if .env file exists
const envPath = path.join(__dirname, '.env');
let envContent = '';

if (fs.existsSync(envPath)) {
  envContent = fs.readFileSync(envPath, 'utf8');
  console.log('✅ Found existing .env file');
} else {
  console.log('❌ No .env file found. Creating new one...');
}

// Function to update or add email configuration
function updateEnvFile() {
  console.log('\n📝 Email Configuration Setup');
  console.log('============================');
  console.log('You need to configure Gmail SMTP for email notifications.');
  console.log('\n📋 Steps to get Gmail App Password:');
  console.log('1. Go to your Google Account settings');
  console.log('2. Enable 2-Factor Authentication (if not already enabled)');
  console.log('3. Go to Security → App passwords');
  console.log('4. Select "Mail" and "Other (Custom name)"');
  console.log('5. Enter "Invensis Hiring Portal"');
  console.log('6. Copy the generated 16-character password\n');

  rl.question('Enter your Gmail address: ', (email) => {
    rl.question('Enter your Gmail App Password (16 characters): ', (password) => {
      // Validate email format
      if (!email.includes('@gmail.com')) {
        console.log('❌ Please enter a valid Gmail address');
        rl.close();
        return;
      }

      // Validate password length
      if (password.length < 16 || password.length > 16) {
        console.log(`❌ App Password should be exactly 16 characters (you entered ${password.length})`);
        console.log('💡 Make sure to copy the password without any spaces');
        console.log('💡 Example: "abcd efgh ijkl mnop" should be "abcdefghijklmnop"');
        rl.close();
        return;
      }

      // Update .env content
      let newEnvContent = envContent;
      
      // Remove existing email config if present
      newEnvContent = newEnvContent.replace(/EMAIL_USER=.*\n/g, '');
      newEnvContent = newEnvContent.replace(/EMAIL_PASS=.*\n/g, '');
      
      // Add new email config
      newEnvContent += `\n# Email Configuration (Gmail)\nEMAIL_USER=${email}\nEMAIL_PASS=${password}\n`;

      // Write to .env file
      fs.writeFileSync(envPath, newEnvContent);
      
      console.log('\n✅ Email configuration updated successfully!');
      console.log(`📧 Email: ${email}`);
      console.log('🔐 App Password: [Hidden]');
      console.log('\n🔄 Please restart your server to apply the changes.');
      console.log('💡 Run: node server/index.js');
      
      rl.close();
    });
  });
}

// Function to test email configuration
function testEmailConfig() {
  console.log('\n🧪 Testing Email Configuration');
  console.log('==============================');
  
  // Check if email config exists in .env
  const emailUserMatch = envContent.match(/EMAIL_USER=(.+)/);
  const emailPassMatch = envContent.match(/EMAIL_PASS=(.+)/);
  
  if (!emailUserMatch || !emailPassMatch) {
    console.log('❌ Email configuration not found in .env file');
    console.log('💡 Run this script again to configure email settings');
    rl.close();
    return;
  }
  
  const emailUser = emailUserMatch[1];
  const emailPass = emailPassMatch[1];
  
  console.log('✅ Email configuration found:');
  console.log(`📧 Email: ${emailUser}`);
  console.log('🔐 App Password: [Hidden]');
  console.log('\n💡 To test email functionality:');
  console.log('1. Start the server: node server/index.js');
  console.log('2. Check server logs for email configuration status');
  console.log('3. Try assigning a candidate to test email sending');
  
  rl.close();
}

// Main menu
console.log('What would you like to do?');
console.log('1. Configure email settings');
console.log('2. Test email configuration');
console.log('3. Exit');

rl.question('\nEnter your choice (1-3): ', (choice) => {
  switch (choice) {
    case '1':
      updateEnvFile();
      break;
    case '2':
      testEmailConfig();
      break;
    case '3':
      console.log('👋 Goodbye!');
      rl.close();
      break;
    default:
      console.log('❌ Invalid choice. Please enter 1, 2, or 3.');
      rl.close();
      break;
  }
}); 