const mongoose = require('mongoose');

const assignmentSchema = new mongoose.Schema({
  candidate: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Candidate',
    required: true
  },
  assignedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  assignedTo: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  managerEmail: {
    type: String,
    required: true,
    trim: true,
    lowercase: true
  },
  managerName: {
    type: String,
    trim: true
  },
  scheduleDate: {
    type: Date
  },
  status: {
    type: String,
    enum: ['Assigned', 'Under Review', 'Interview Scheduled', 'Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR', 'Feedback Submitted'],
    default: 'Assigned'
  },
  feedback: {
    type: String,
    trim: true
  },
  interviewDate: {
    type: Date
  },
  interviewNotes: {
    type: String,
    trim: true
  },
  managerComments: {
    type: String,
    trim: true
  },
  hrComments: {
    type: String,
    trim: true
  },
  feedbackSubmitted: {
    type: Boolean,
    default: false
  },
  assignedAt: {
    type: Date,
    default: Date.now
  },
  reviewedAt: {
    type: Date
  }
});

module.exports = mongoose.model('Assignment', assignmentSchema); 