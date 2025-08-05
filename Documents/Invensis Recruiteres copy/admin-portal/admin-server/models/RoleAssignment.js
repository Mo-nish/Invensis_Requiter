const mongoose = require('mongoose');

// Role limits configuration
const ROLE_LIMITS = {
  'Admin': 5,
  'HR': 10,
  'Manager': 20,
  'Board Member': 10
};

const roleAssignmentSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    lowercase: true,
    trim: true
  },
  role: {
    type: String,
    required: true,
    enum: ['HR', 'Manager', 'Board Member']
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
}, {
  timestamps: true
});

// Indexes for efficient queries
roleAssignmentSchema.index({ email: 1, role: 1 }, { unique: true });
roleAssignmentSchema.index({ status: 1 });
roleAssignmentSchema.index({ isActive: 1 });

// Static method to check role limits
roleAssignmentSchema.statics.checkRoleLimit = async function(role) {
  const limit = ROLE_LIMITS[role];
  if (!limit) {
    throw new Error(`Invalid role: ${role}`);
  }
  
  const currentCount = await this.countDocuments({ 
    role, 
    isActive: true 
  });
  
  return {
    currentCount,
    limit,
    canAdd: currentCount < limit
  };
};

// Static method to get role limits
roleAssignmentSchema.statics.getRoleLimits = function() {
  return ROLE_LIMITS;
};

module.exports = mongoose.model('RoleAssignment', roleAssignmentSchema); 