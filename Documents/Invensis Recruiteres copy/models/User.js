const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  designation: {
    type: String,
    required: false, // Made optional - will be set by admin
    enum: ['HR', 'Manager', 'Board Member']
  },
  password: {
    type: String,
    required: true,
    minlength: 8 // Increased minimum length
  },
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Static method to check if email is authorized
userSchema.statics.isEmailAuthorized = async function(email) {
  try {
    const RoleAssignment = mongoose.model('RoleAssignment');
    const assignment = await RoleAssignment.findOne({ 
      email: email.toLowerCase(), 
      isActive: true 
    });
    return assignment;
  } catch (error) {
    console.error('Role assignment check error:', error);
    return null;
  }
};

module.exports = mongoose.model('User', userSchema); 