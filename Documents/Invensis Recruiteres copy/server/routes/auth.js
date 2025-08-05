const express = require('express');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const { auth } = require('../middleware/auth');
const mongoose = require('mongoose');

const router = express.Router();

// Register new user
router.post('/register', [
  body('name').trim().isLength({ min: 2 }).withMessage('Name must be at least 2 characters long'),
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[A-Za-z])(?=.*\d)/)
    .withMessage('Password must contain at least one letter and one number'),
  body('confirmPassword').custom((value, { req }) => {
    if (value !== req.body.password) {
      throw new Error('Password confirmation does not match password');
    }
    return true;
  }),
  body('invitationToken').optional().isString().withMessage('Invalid invitation token')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, email, password, invitationToken } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User with this email already exists' });
    }

    let roleAssignment = null;
    let role = null;

    // If token is provided, verify it
    if (invitationToken) {
      try {
        const decoded = jwt.verify(invitationToken, process.env.JWT_SECRET || 'your-secret-key');
        
        if (decoded.type !== 'invitation') {
          return res.status(400).json({ message: 'Invalid invitation token' });
        }

        if (decoded.email.toLowerCase() !== email.toLowerCase()) {
          return res.status(400).json({ message: 'Email does not match invitation' });
        }

        role = decoded.role;

        // Check if role assignment exists and is active
        const RoleAssignment = mongoose.model('RoleAssignment');
        roleAssignment = await RoleAssignment.findOne({ 
          email: email.toLowerCase(), 
          role,
          isActive: true 
        });

        if (!roleAssignment) {
          return res.status(403).json({ 
            message: 'Invitation not found or expired. Please contact admin for a new invitation.' 
          });
        }

      } catch (tokenError) {
        return res.status(400).json({ 
          message: 'Invalid or expired invitation token. Please contact admin for a new invitation.' 
        });
      }
    } else {
      // No token provided - check if email is authorized by admin
      try {
        const RoleAssignment = mongoose.model('RoleAssignment');
        roleAssignment = await RoleAssignment.findOne({ 
          email: email.toLowerCase(), 
          isActive: true 
        });
        
        if (!roleAssignment) {
          return res.status(403).json({ 
            message: 'Email not authorized. Please contact the admin to get access.' 
          });
        }

        role = roleAssignment.role;
      } catch (error) {
        console.error('Role verification error:', error);
        return res.status(500).json({ message: 'Role verification failed' });
      }
    }

    // Create new user
    const user = new User({
      name,
      email,
      designation: role,
      password
    });

    await user.save();

    // Update role assignment as registered
    if (roleAssignment) {
      await mongoose.model('RoleAssignment').findOneAndUpdate(
        { email: email.toLowerCase(), role: roleAssignment.role },
        { 
          status: 'active',
          registeredAt: new Date(),
          lastLogin: new Date()
        }
      );
    }

    // Generate JWT token
    const jwtToken = jwt.sign(
      { userId: user._id, email: user.email, designation: user.designation },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'Registration successful',
      token: jwtToken,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        designation: user.designation
      }
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Registration failed' });
  }
});

// Login user
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

    // Find user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Check password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(403).json({ message: 'Account is deactivated. Please contact admin.' });
    }

    // Update last login
    user.lastLogin = new Date();
    await user.save();

    // Generate JWT token
    const jwtToken = jwt.sign(
      { userId: user._id, email: user.email, designation: user.designation },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({
      message: 'Login successful',
      token: jwtToken,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        designation: user.designation
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Login failed' });
  }
});

// Get current user
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.userId).select('-password');
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ message: 'Failed to get user' });
  }
});

module.exports = router; 