const express = require('express');
const { adminAuth } = require('../middleware/auth');
const RoleAssignment = require('../models/RoleAssignment');

const router = express.Router();

// Get dashboard overview
router.get('/overview', adminAuth, async (req, res) => {
  try {
    // Get role assignment stats
    const roleStats = await RoleAssignment.aggregate([
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

    // Get recent role assignments
    const recentAssignments = await RoleAssignment.find()
      .populate('invitedBy', 'name email')
      .sort({ invitedAt: -1 })
      .limit(10);

    // Get system stats (if we have access to main app models)
    let systemStats = {
      totalCandidates: 0,
      totalAssignments: 0,
      totalUsers: 0
    };

    try {
      // Try to get stats from main app models
      const mongoose = require('mongoose');
      
      // Check if models exist (they might not if admin server is separate)
      if (mongoose.models.Candidate) {
        systemStats.totalCandidates = await mongoose.models.Candidate.countDocuments();
      }
      
      if (mongoose.models.Assignment) {
        systemStats.totalAssignments = await mongoose.models.Assignment.countDocuments();
      }
      
      if (mongoose.models.User) {
        systemStats.totalUsers = await mongoose.models.User.countDocuments();
      }
    } catch (error) {
      console.log('Could not fetch system stats:', error.message);
    }

    res.json({
      roleStats: roleStats.reduce((acc, stat) => {
        acc[stat._id] = {
          total: stat.total,
          active: stat.active,
          pending: stat.pending,
          registered: stat.registered
        };
        return acc;
      }, {}),
      recentAssignments,
      systemStats
    });
  } catch (error) {
    console.error('Get dashboard overview error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get role-specific analytics
router.get('/analytics/:role', adminAuth, async (req, res) => {
  try {
    const { role } = req.params;
    
    if (!['HR', 'Manager', 'Board Member'].includes(role)) {
      return res.status(400).json({ message: 'Invalid role' });
    }

    const assignments = await RoleAssignment.find({ role })
      .populate('invitedBy', 'name email')
      .sort({ invitedAt: -1 });

    const stats = {
      total: assignments.length,
      active: assignments.filter(a => a.isActive).length,
      pending: assignments.filter(a => a.status === 'pending').length,
      registered: assignments.filter(a => a.registeredAt).length,
      inactive: assignments.filter(a => !a.isActive).length
    };

    // Get monthly trends
    const monthlyTrends = await RoleAssignment.aggregate([
      { $match: { role } },
      {
        $group: {
          _id: {
            year: { $year: '$invitedAt' },
            month: { $month: '$invitedAt' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } }
    ]);

    res.json({
      role,
      stats,
      assignments,
      monthlyTrends
    });
  } catch (error) {
    console.error('Get role analytics error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get email status
router.get('/email-status', adminAuth, async (req, res) => {
  try {
    const { verifyEmailConfig } = require('../utils/emailService');
    const isConfigured = await verifyEmailConfig();
    
    res.json({
      emailConfigured: isConfigured,
      emailUser: process.env.EMAIL_USER ? 'Configured' : 'Not configured',
      emailPass: process.env.EMAIL_PASS ? 'Configured' : 'Not configured'
    });
  } catch (error) {
    console.error('Get email status error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 