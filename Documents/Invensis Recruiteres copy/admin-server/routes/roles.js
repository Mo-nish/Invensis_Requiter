const express = require('express');
const { body, validationResult } = require('express-validator');
const RoleAssignment = require('../models/RoleAssignment');
const { adminAuth } = require('../middleware/auth');
const { sendRoleAssignmentEmail } = require('../utils/emailService');

const router = express.Router();

// Get all role assignments
router.get('/', adminAuth, async (req, res) => {
  try {
    const assignments = await RoleAssignment.find()
      .populate('invitedBy', 'name email')
      .sort({ invitedAt: -1 });

    // Group by role
    const groupedAssignments = {
      'HR': assignments.filter(a => a.role === 'HR'),
      'Manager': assignments.filter(a => a.role === 'Manager'),
      'Board Member': assignments.filter(a => a.role === 'Board Member')
    };

    res.json({ assignments: groupedAssignments });
  } catch (error) {
    console.error('Get role assignments error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Add role assignment
router.post('/', adminAuth, [
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email'),
  body('role').isIn(['HR', 'Manager', 'Board Member']).withMessage('Invalid role')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, role } = req.body;

    // Check if assignment already exists
    const existingAssignment = await RoleAssignment.findOne({ email });
    if (existingAssignment) {
      return res.status(400).json({ 
        message: `Email ${email} is already assigned to role: ${existingAssignment.role}` 
      });
    }

    // Create new role assignment
    const assignment = new RoleAssignment({
      email: email.toLowerCase(),
      role,
      invitedBy: req.admin._id,
      status: 'pending'
    });

    await assignment.save();

    // Send email notification
    const emailResult = await sendRoleAssignmentEmail(email, role, req.admin.name);

    res.status(201).json({
      message: 'Role assignment created successfully',
      assignment: {
        id: assignment._id,
        email: assignment.email,
        role: assignment.role,
        status: assignment.status,
        invitedAt: assignment.invitedAt
      },
      emailSent: emailResult.success,
      emailMessage: emailResult.success ? 'Email notification sent' : emailResult.error
    });
  } catch (error) {
    console.error('Create role assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update role assignment
router.put('/:id', adminAuth, [
  body('status').optional().isIn(['pending', 'active', 'inactive']).withMessage('Invalid status'),
  body('isActive').optional().isBoolean().withMessage('isActive must be boolean')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const assignment = await RoleAssignment.findById(req.params.id);
    if (!assignment) {
      return res.status(404).json({ message: 'Role assignment not found' });
    }

    // Update fields
    if (req.body.status) assignment.status = req.body.status;
    if (req.body.isActive !== undefined) assignment.isActive = req.body.isActive;

    await assignment.save();

    res.json({
      message: 'Role assignment updated successfully',
      assignment: {
        id: assignment._id,
        email: assignment.email,
        role: assignment.role,
        status: assignment.status,
        isActive: assignment.isActive
      }
    });
  } catch (error) {
    console.error('Update role assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete role assignment
router.delete('/:id', adminAuth, async (req, res) => {
  try {
    const assignment = await RoleAssignment.findById(req.params.id);
    if (!assignment) {
      return res.status(404).json({ message: 'Role assignment not found' });
    }

    await assignment.deleteOne();

    res.json({ message: 'Role assignment deleted successfully' });
  } catch (error) {
    console.error('Delete role assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get role statistics
router.get('/stats', adminAuth, async (req, res) => {
  try {
    const stats = await RoleAssignment.aggregate([
      {
        $group: {
          _id: '$role',
          total: { $sum: 1 },
          active: { $sum: { $cond: ['$isActive', 1, 0] } },
          pending: { $sum: { $cond: [{ $eq: ['$status', 'pending'] }, 1, 0] } },
          registered: { $sum: { $cond: ['$registeredAt', 1, 0] } }
        }
      }
    ]);

    const formattedStats = {};
    stats.forEach(stat => {
      formattedStats[stat._id] = {
        total: stat.total,
        active: stat.active,
        pending: stat.pending,
        registered: stat.registered
      };
    });

    res.json({ stats: formattedStats });
  } catch (error) {
    console.error('Get role stats error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 