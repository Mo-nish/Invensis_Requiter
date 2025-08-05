const express = require('express');
const { body, validationResult } = require('express-validator');
const RoleAssignment = require('../models/RoleAssignment');
const Admin = require('../models/Admin');
const { adminAuth } = require('../middleware/auth');
const { sendRoleAssignmentEmail } = require('../utils/emailService');

const router = express.Router();

// Get all role assignments
router.get('/', adminAuth, async (req, res) => {
  try {
    const assignments = await RoleAssignment.find()
      .populate('invitedBy', 'name email')
      .sort({ createdAt: -1 });
    
    res.json(assignments);
  } catch (error) {
    console.error('Error fetching role assignments:', error);
    res.status(500).json({ message: 'Failed to fetch role assignments' });
  }
});

// Get role limits
router.get('/limits', adminAuth, async (req, res) => {
  try {
    const limits = RoleAssignment.getRoleLimits();
    const currentCounts = {};
    
    // Get current counts for each role
    for (const role of Object.keys(limits)) {
      const count = await RoleAssignment.countDocuments({ 
        role, 
        isActive: true 
      });
      currentCounts[role] = count;
    }
    
    res.json({
      limits,
      currentCounts
    });
  } catch (error) {
    console.error('Error fetching role limits:', error);
    res.status(500).json({ message: 'Failed to fetch role limits' });
  }
});

// Create new role assignment
router.post('/', adminAuth, [
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email'),
  body('role').isIn(['HR', 'Manager', 'Board Member']).withMessage('Role must be HR, Manager, or Board Member')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, role } = req.body;

    // Check if assignment already exists
    const existingAssignment = await RoleAssignment.findOne({ 
      email: email.toLowerCase(), 
      role 
    });

    if (existingAssignment) {
      return res.status(400).json({ 
        message: `User ${email} is already assigned to ${role} role` 
      });
    }

    // Check role limits
    console.log(`🔍 Checking role limit for ${role}...`);
    const limitCheck = await RoleAssignment.checkRoleLimit(role);
    console.log(`📊 Role limit check result:`, limitCheck);
    
    if (!limitCheck.canAdd) {
      console.log(`❌ Role limit reached for ${role}. Current: ${limitCheck.currentCount}/${limitCheck.limit}`);
      return res.status(400).json({ 
        message: `Role limit reached for ${role}. Current: ${limitCheck.currentCount}/${limitCheck.limit}` 
      });
    }
    
    console.log(`✅ Role limit check passed for ${role}`);

    // Create new role assignment
    const assignment = new RoleAssignment({
      email: email.toLowerCase(),
      role,
      invitedBy: req.adminId
    });

    await assignment.save();

    // Send invitation email
    let emailSent = false;
    let emailMessage = '';
    
    try {
      await sendRoleAssignmentEmail(email, role);
      emailSent = true;
    } catch (emailError) {
      console.error('❌ Role assignment email failed:', emailError);
      emailMessage = emailError.message;
    }

    res.status(201).json({
      message: 'Role assignment created successfully',
      assignment,
      emailSent,
      emailMessage
    });

  } catch (error) {
    console.error('Error creating role assignment:', error);
    res.status(500).json({ message: 'Failed to create role assignment' });
  }
});

// Update role assignment
router.put('/:id', adminAuth, [
  body('status').optional().isIn(['pending', 'active', 'inactive']),
  body('isActive').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = req.body;

    const assignment = await RoleAssignment.findByIdAndUpdate(
      id,
      updateData,
      { new: true }
    );

    if (!assignment) {
      return res.status(404).json({ message: 'Role assignment not found' });
    }

    res.json(assignment);
  } catch (error) {
    console.error('Error updating role assignment:', error);
    res.status(500).json({ message: 'Failed to update role assignment' });
  }
});

// Delete role assignment
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const { id } = req.params;
    
    const assignment = await RoleAssignment.findByIdAndDelete(id);
    
    if (!assignment) {
      return res.status(404).json({ message: 'Role assignment not found' });
    }

    res.json({ message: 'Role assignment deleted successfully' });
  } catch (error) {
    console.error('Error deleting role assignment:', error);
    res.status(500).json({ message: 'Failed to delete role assignment' });
  }
});

module.exports = router; 