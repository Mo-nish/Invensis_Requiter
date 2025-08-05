const express = require('express');
const { body, validationResult } = require('express-validator');
const Assignment = require('../models/Assignment');
const Candidate = require('../models/Candidate');
const User = require('../models/User');
const { auth, requireRole } = require('../middleware/auth');
const { sendAssignmentEmail, sendStatusUpdateEmail } = require('../utils/emailService');

const router = express.Router();

// Test email configuration (for debugging)
router.post('/test-email', auth, requireRole(['HR']), [
  body('testEmail').isEmail().withMessage('Test email address is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { testEmail } = req.body;
    
    console.log('🧪 Testing email configuration...');
    const emailResult = await sendAssignmentEmail(
      testEmail,
      'Test Candidate',
      'REF123456789',
      'Test HR',
      new Date(),
      'Test Manager'
    );

    if (emailResult.success) {
      res.json({ 
        message: 'Test email sent successfully', 
        messageId: emailResult.messageId 
      });
    } else {
      res.status(500).json({ 
        message: 'Test email failed', 
        error: emailResult.reason || emailResult.error 
      });
    }
  } catch (error) {
    console.error('Test email error:', error);
    res.status(500).json({ message: 'Server error during test email' });
  }
});

// Assign candidate to manager (HR only)
router.post('/', auth, requireRole(['HR']), [
  body('candidateId').notEmpty().withMessage('Candidate ID is required'),
  body('managerEmail').isEmail().normalizeEmail().withMessage('Please provide a valid manager email'),
  body('managerName').optional().trim(),
  body('scheduleDate').optional().isISO8601().withMessage('Schedule date must be a valid date')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { candidateId, managerEmail, managerName, scheduleDate } = req.body;

    // Check if candidate exists
    const candidate = await Candidate.findById(candidateId);
    if (!candidate) {
      return res.status(404).json({ message: 'Candidate not found' });
    }

    // Check if candidate is already assigned
    const existingAssignment = await Assignment.findOne({ candidate: candidateId });
    if (existingAssignment) {
      return res.status(400).json({ message: 'Candidate is already assigned to a manager' });
    }

    // Find manager by email
    const manager = await User.findOne({ email: managerEmail, designation: 'Manager' });
    if (!manager) {
      return res.status(404).json({ message: 'Manager not found with this email' });
    }

    // Create assignment
    const assignment = new Assignment({
      candidate: candidateId,
      assignedBy: req.user._id,
      assignedTo: manager._id,
      managerEmail,
      managerName: managerName || manager.name,
      scheduleDate: scheduleDate ? new Date(scheduleDate) : null
    });

    await assignment.save();

    // Update candidate status
    candidate.status = 'Assigned';
    await candidate.save();

    // Send email notification to manager
    console.log('📧 Triggering email notification...');
    const emailResult = await sendAssignmentEmail(
      managerEmail,
      candidate.fullName,
      candidate.referenceNumber,
      req.user.name,
      scheduleDate,
      managerName
    );

    // Log email result
    if (emailResult.success) {
      console.log('✅ Email sent successfully:', emailResult.messageId);
    } else {
      console.log('❌ Email failed:', emailResult.reason || emailResult.error);
    }

    res.status(201).json({
      message: 'Candidate assigned successfully',
      emailSent: emailResult.success,
      emailMessage: emailResult.success ? 'Email notification sent successfully' : (emailResult.reason || emailResult.error),
      assignment: {
        id: assignment._id,
        candidate: {
          id: candidate._id,
          name: candidate.fullName,
          referenceNumber: candidate.referenceNumber
        },
        manager: {
          id: manager._id,
          name: manager.name,
          email: manager.email
        },
        status: assignment.status,
        assignedAt: assignment.assignedAt
      }
    });
  } catch (error) {
    console.error('Assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get assignments (HR can see all, Manager can see their own)
router.get('/', auth, async (req, res) => {
  try {
    let assignments;
    
    if (req.user.designation === 'HR') {
      // HR can see all assignments
      assignments = await Assignment.find()
        .populate('candidate')
        .populate('assignedBy', 'name email')
        .populate('assignedTo', 'name email')
        .sort({ assignedAt: -1 });
    } else {
      // Manager can only see their assignments
      assignments = await Assignment.find({ assignedTo: req.user._id })
        .populate('candidate')
        .populate('assignedBy', 'name email')
        .populate('assignedTo', 'name email')
        .sort({ assignedAt: -1 });
    }

    res.json({ assignments });
  } catch (error) {
    console.error('Get assignments error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get assignment by ID
router.get('/:id', auth, async (req, res) => {
  try {
    const assignment = await Assignment.findById(req.params.id)
      .populate('candidate')
      .populate('assignedBy', 'name email')
      .populate('assignedTo', 'name email');

    if (!assignment) {
      return res.status(404).json({ message: 'Assignment not found' });
    }

    // Check access permissions
    if (req.user.designation === 'Manager' && assignment.assignedTo._id.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Access denied' });
    }

    res.json({ assignment });
  } catch (error) {
    console.error('Get assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update assignment (Manager can update status and feedback)
router.put('/:id', auth, requireRole(['Manager']), [
  body('status').optional().isIn(['Under Review', 'Interview Scheduled', 'Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR', 'Feedback Submitted']).withMessage('Invalid status'),
  body('feedback').optional().trim(),
  body('interviewDate').optional().isISO8601().withMessage('Interview date must be a valid date'),
  body('interviewNotes').optional().trim(),
  body('managerComments').optional().trim()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const assignment = await Assignment.findById(req.params.id)
      .populate('candidate')
      .populate('assignedBy', 'name email');

    if (!assignment) {
      return res.status(404).json({ message: 'Assignment not found' });
    }

    // Check if manager owns this assignment
    if (assignment.assignedTo.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Access denied' });
    }

    const {
      status,
      feedback,
      interviewDate,
      interviewNotes,
      managerComments
    } = req.body;

    // Update assignment
    if (status) {
      assignment.status = status;
      assignment.reviewedAt = new Date();
      
      // Set feedbackSubmitted to true if feedback is provided or status indicates feedback was submitted
      if (feedback || status === 'Feedback Submitted' || 
          ['Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR'].includes(status)) {
        assignment.feedbackSubmitted = true;
      }
    }
    if (feedback) assignment.feedback = feedback;
    if (interviewDate) assignment.interviewDate = new Date(interviewDate);
    if (interviewNotes) assignment.interviewNotes = interviewNotes;
    if (managerComments) assignment.managerComments = managerComments;

    await assignment.save();

    // Update candidate status
    const candidate = await Candidate.findById(assignment.candidate);
    if (candidate && status) {
      candidate.status = status;
      await candidate.save();
    }

    // Send email notification to HR if status changed
    if (status && status !== 'Under Review') {
      console.log('📧 Triggering status update email...');
      const emailResult = await sendStatusUpdateEmail(
        assignment.assignedBy.email,
        candidate.name,
        candidate.referenceNumber,
        status,
        req.user.name
      );

      // Log email result
      if (emailResult.success) {
        console.log('✅ Status update email sent successfully:', emailResult.messageId);
      } else {
        console.log('❌ Status update email failed:', emailResult.reason || emailResult.error);
      }
    }

    res.json({
      message: 'Assignment updated successfully',
      assignment
    });
  } catch (error) {
    console.error('Update assignment error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// HR can add comments to assignment
router.put('/:id/comments', auth, requireRole(['HR']), [
  body('hrComments').trim().notEmpty().withMessage('Comments are required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const assignment = await Assignment.findById(req.params.id);

    if (!assignment) {
      return res.status(404).json({ message: 'Assignment not found' });
    }

    // Check if HR owns this assignment
    if (assignment.assignedBy.toString() !== req.user._id.toString()) {
      return res.status(403).json({ message: 'Access denied' });
    }

    assignment.hrComments = req.body.hrComments;
    await assignment.save();

    res.json({
      message: 'Comments added successfully',
      assignment
    });
  } catch (error) {
    console.error('Add comments error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get assignment statistics
router.get('/stats/overview', auth, async (req, res) => {
  try {
    let query = {};
    
    if (req.user.designation === 'Manager') {
      query.assignedTo = req.user._id;
    }

    const stats = await Assignment.aggregate([
      { $match: query },
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 }
        }
      }
    ]);

    const total = await Assignment.countDocuments(query);

    res.json({
      stats,
      total
    });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 