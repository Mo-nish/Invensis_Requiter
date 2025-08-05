const express = require('express');
const { body, validationResult } = require('express-validator');
const Admin = require('../models/Admin');
const { adminAuth, generateAdminToken } = require('../middleware/auth');
const { sendAdminRegistrationEmail, verifyEmailConfig } = require('../utils/emailService');

const router = express.Router();

// Admin Registration
router.post('/register', [
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid Gmail address'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters long'),
  body('name').trim().isLength({ min: 2 }).withMessage('Name must be at least 2 characters long')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, name } = req.body;

    // Check if admin already exists
    const existingAdmin = await Admin.findOne({ email });
    if (existingAdmin) {
      return res.status(400).json({ message: 'Admin with this email already exists' });
    }

    // Create new admin
    const admin = new Admin({
      email,
      password,
      name,
      role: 'admin'
    });

    await admin.save();

    // Send confirmation email
    const emailResult = await sendAdminRegistrationEmail(email, name);

    res.status(201).json({
      message: 'Admin registered successfully',
      admin: {
        id: admin._id,
        email: admin.email,
        name: admin.name,
        role: admin.role
      },
      emailSent: emailResult.success
    });
  } catch (error) {
    console.error('Admin registration error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Admin Login
router.post('/login', [
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email'),
  body('password').notEmpty().withMessage('Password is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password } = req.body;

    // Find admin
    const admin = await Admin.findOne({ email });
    if (!admin || !admin.isActive) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Check password
    const isPasswordValid = await admin.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Update last login
    admin.lastLogin = new Date();
    await admin.save();

    // Generate token
    const token = generateAdminToken(admin._id);

    // Set cookie
    res.cookie('admin_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    });

    res.json({
      message: 'Admin login successful',
      admin: {
        id: admin._id,
        email: admin.email,
        name: admin.name,
        role: admin.role
      },
      token
    });
  } catch (error) {
    console.error('Admin login error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Admin Logout
router.post('/logout', adminAuth, (req, res) => {
  try {
    // Clear admin token cookie
    res.clearCookie('admin_token', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict'
    });

    res.json({ 
      message: 'Admin logged out successfully',
      redirectTo: '/admin/login'
    });
  } catch (error) {
    console.error('Admin logout error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get current admin
router.get('/me', adminAuth, (req, res) => {
  res.json({
    admin: {
      id: req.admin._id,
      email: req.admin.email,
      name: req.admin.name,
      role: req.admin.role,
      lastLogin: req.admin.lastLogin
    }
  });
});

// Check email configuration
router.get('/email-status', async (req, res) => {
  const isConfigured = await verifyEmailConfig();
  res.json({
    emailConfigured: isConfigured,
    emailUser: process.env.EMAIL_USER ? 'Configured' : 'Not configured',
    emailPass: process.env.EMAIL_PASS ? 'Configured' : 'Not configured'
  });
});

module.exports = router; 