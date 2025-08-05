const mongoose = require('mongoose');

const candidateSchema = new mongoose.Schema({
  referenceNumber: {
    type: String,
    unique: true,
    required: false
  },
  firstName: {
    type: String,
    required: true,
    trim: true
  },
  lastName: {
    type: String,
    required: true,
    trim: true
  },
  phoneNumber: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    trim: true,
    lowercase: true
  },
  gender: {
    type: String,
    required: true,
    enum: ['Male', 'Female', 'Other']
  },
  dateOfBirth: {
    type: Date,
    required: true
  },
  education: {
    type: String,
    required: true,
    trim: true
  },
  experience: {
    type: String,
    required: true,
    trim: true
  },
  technicalTestRating: {
    type: Number,
    min: 1,
    max: 10,
    required: false
  },
  hrInterviewRating: {
    type: Number,
    min: 1,
    max: 10,
    required: false
  },
  hrReview: {
    type: String,
    required: false,
    trim: true
  },
  image: {
    type: String,
    required: true
  },
  resume: {
    type: String,
    required: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    enum: ['New', 'Assigned', 'Under Review', 'Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR'],
    default: 'New'
  }
});

// Generate reference number before saving
candidateSchema.pre('save', function(next) {
  if (!this.referenceNumber) {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    this.referenceNumber = `REF${timestamp}${random}`;
  }
  next();
});

// Virtual for full name
candidateSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Virtual for age calculation
candidateSchema.virtual('age').get(function() {
  if (!this.dateOfBirth) return null;
  const today = new Date();
  const birthDate = new Date(this.dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
});

// Ensure virtuals are serialized
candidateSchema.set('toJSON', { virtuals: true });
candidateSchema.set('toObject', { virtuals: true });

module.exports = mongoose.model('Candidate', candidateSchema); 