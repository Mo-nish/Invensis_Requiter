const mongoose = require('mongoose');

const roleAssignmentSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  role: {
    type: String,
    enum: ['HR', 'Manager', 'Board Member'],
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'active', 'inactive'],
    default: 'pending'
  },
  invitedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Admin',
    required: true
  },
  invitedAt: {
    type: Date,
    default: Date.now
  },
  registeredAt: {
    type: Date,
    default: null
  },
  lastLogin: {
    type: Date,
    default: null
  },
  isActive: {
    type: Boolean,
    default: true
  }
});

// Index for efficient queries
roleAssignmentSchema.index({ email: 1, role: 1 });
roleAssignmentSchema.index({ status: 1 });

module.exports = mongoose.model('RoleAssignment', roleAssignmentSchema); 