const express = require('express');
const RoleAssignment = require('../models/RoleAssignment');
const { adminAuth } = require('../middleware/auth');

const router = express.Router();

// Get dashboard overview
router.get('/overview', adminAuth, async (req, res) => {
  try {
    // Get role statistics
    const roleStats = await RoleAssignment.aggregate([
      {
        $group: {
          _id: '$role',
          total: { $sum: 1 },
          active: { $sum: { $cond: [{ $eq: ['$isActive', true] }, 1, 0] } },
          pending: { $sum: { $cond: [{ $eq: ['$status', 'pending'] }, 1, 0] } },
          registered: { $sum: { $cond: [{ $ne: ['$registeredAt', null] }, 1, 0] } }
        }
      }
    ]);

    const formattedRoleStats = {};
    roleStats.forEach(stat => {
      formattedRoleStats[stat._id] = {
        total: stat.total,
        active: stat.active,
        pending: stat.pending,
        registered: stat.registered
      };
    });

    // Get recent assignments
    const recentAssignments = await RoleAssignment.find()
      .populate('invitedBy', 'name email')
      .sort({ invitedAt: -1 })
      .limit(10);

    // Get system statistics (if main app models are accessible)
    let systemStats = {
      totalUsers: 0,
      totalAssignments: await RoleAssignment.countDocuments(),
      totalCandidates: 0
    };

    // Try to get main app statistics if models are accessible
    try {
      const mongoose = require('mongoose');
      
      // Check if User model exists (from main app)
      if (mongoose.models.User) {
        systemStats.totalUsers = await mongoose.models.User.countDocuments();
      }
      
      // Check if Candidate model exists (from main app)
      if (mongoose.models.Candidate) {
        systemStats.totalCandidates = await mongoose.models.Candidate.countDocuments();
      }
    } catch (error) {
      console.log('Main app models not accessible, using default stats');
    }

    res.json({
      roleStats: formattedRoleStats,
      recentAssignments,
      systemStats
    });

  } catch (error) {
    console.error('Get dashboard overview error:', error);
    res.status(500).json({ message: 'Failed to fetch dashboard overview' });
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

    res.json({
      role,
      stats,
      assignments
    });

  } catch (error) {
    console.error('Get role analytics error:', error);
    res.status(500).json({ message: 'Failed to fetch role analytics' });
  }
});

module.exports = router; 