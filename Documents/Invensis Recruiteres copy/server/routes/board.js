const express = require('express');
const { auth, requireRole } = require('../middleware/auth');
const Candidate = require('../models/Candidate');
const Assignment = require('../models/Assignment');
const User = require('../models/User');

const router = express.Router();

// Get comprehensive clusters data (Board Members only)
router.get('/candidates', auth, requireRole(['Board Member']), async (req, res) => {
  try {
    // Get all candidates with full details
    const candidates = await Candidate.find()
      .populate('createdBy', 'name email')
      .sort({ createdAt: -1 });

    // Get all assignments with populated data
    const assignments = await Assignment.find()
      .populate('candidate')
      .populate('assignedBy', 'name email')
      .populate('assignedTo', 'name email')
      .sort({ assignedAt: -1 });

    // Enrich candidates with assignment data
    const enrichedCandidates = candidates.map(candidate => {
      const assignment = assignments.find(assign => 
        assign.candidate._id.toString() === candidate._id.toString()
      );

      return {
        ...candidate.toObject(),
        assignment: assignment ? {
          id: assignment._id,
          status: assignment.status,
          assignedAt: assignment.assignedAt,
          reviewedAt: assignment.reviewedAt,
          interviewDate: assignment.interviewDate,
          feedback: assignment.feedback,
          managerComments: assignment.managerComments,
          interviewNotes: assignment.interviewNotes,
          assignedBy: assignment.assignedBy,
          assignedTo: assignment.assignedTo,
          feedbackSubmitted: assignment.feedbackSubmitted
        } : null,
        hasAssignment: !!assignment,
        assignmentStatus: assignment?.status || 'Not Assigned',
        assignedTo: assignment?.assignedTo?.name || 'N/A',
        assignedBy: assignment?.assignedBy?.name || 'N/A',
        assignedAt: assignment?.assignedAt || null,
        managerFeedback: assignment?.feedback || null,
        managerComments: assignment?.managerComments || null,
        interviewDate: assignment?.interviewDate || null,
        reviewedAt: assignment?.reviewedAt || null
      };
    });

    res.json({
      candidates: enrichedCandidates,
      assignments: assignments,
      totalCandidates: candidates.length,
      totalAssignments: assignments.length,
      stats: {
        new: candidates.filter(c => c.status === 'New').length,
        assigned: candidates.filter(c => c.status === 'Assigned').length,
        underReview: candidates.filter(c => c.status === 'Under Review').length,
        shortlisted: candidates.filter(c => c.status === 'Shortlisted').length,
        rejected: candidates.filter(c => c.status === 'Rejected').length,
        onHold: candidates.filter(c => c.status === 'On Hold').length,
        reassignedToHR: candidates.filter(c => c.status === 'Reassigned to HR').length
      }
    });
  } catch (error) {
    console.error('Clusters candidates error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get board statistics
router.get('/stats', auth, requireRole(['Board Member']), async (req, res) => {
  try {
    const candidates = await Candidate.find();
    const assignments = await Assignment.find();

    const stats = {
      totalCandidates: candidates.length,
      totalAssignments: assignments.length,
      candidateStatusCounts: candidates.reduce((acc, candidate) => {
        acc[candidate.status] = (acc[candidate.status] || 0) + 1;
        return acc;
      }, {}),
      assignmentStatusCounts: assignments.reduce((acc, assignment) => {
        acc[assignment.status] = (acc[assignment.status] || 0) + 1;
        return acc;
      }, {}),
      ratings: {
        withTechnicalRating: candidates.filter(c => c.technicalTestRating).length,
        withHRRating: candidates.filter(c => c.hrInterviewRating).length,
        withHRReview: candidates.filter(c => c.hrReview).length,
        withManagerFeedback: assignments.filter(a => a.feedback).length
      }
    };

    res.json({ stats });
  } catch (error) {
    console.error('Clusters stats error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get timeline data
router.get('/timeline', auth, requireRole(['Board Member']), async (req, res) => {
  try {
    const candidates = await Candidate.find()
      .populate('createdBy', 'name email')
      .sort({ createdAt: -1 });

    const assignments = await Assignment.find()
      .populate('candidate')
      .populate('assignedBy', 'name email')
      .populate('assignedTo', 'name email')
      .sort({ assignedAt: -1 });

    const timeline = [];

    // Add candidate creation events
    candidates.forEach(candidate => {
      timeline.push({
        id: `candidate-${candidate._id}`,
        type: 'candidate_created',
        candidate: {
          id: candidate._id,
          referenceNumber: candidate.referenceNumber,
          name: `${candidate.firstName} ${candidate.lastName}`,
          status: candidate.status
        },
        createdBy: candidate.createdBy,
        timestamp: candidate.createdAt,
        description: `Candidate ${candidate.referenceNumber} created by ${candidate.createdBy?.name || 'Unknown'}`
      });
    });

    // Add assignment events
    assignments.forEach(assignment => {
      timeline.push({
        id: `assignment-${assignment._id}`,
        type: 'candidate_assigned',
        candidate: {
          id: assignment.candidate._id,
          referenceNumber: assignment.candidate.referenceNumber,
          name: `${assignment.candidate.firstName} ${assignment.candidate.lastName}`,
          status: assignment.candidate.status
        },
        assignment: {
          id: assignment._id,
          status: assignment.status,
          assignedTo: assignment.assignedTo,
          assignedBy: assignment.assignedBy
        },
        timestamp: assignment.assignedAt,
        description: `Candidate ${assignment.candidate.referenceNumber} assigned to ${assignment.assignedTo?.name || 'Unknown'} by ${assignment.assignedBy?.name || 'Unknown'}`
      });

      // Add review events if feedback was submitted
      if (assignment.reviewedAt) {
        timeline.push({
          id: `review-${assignment._id}`,
          type: 'feedback_submitted',
          candidate: {
            id: assignment.candidate._id,
            referenceNumber: assignment.candidate.referenceNumber,
            name: `${assignment.candidate.firstName} ${assignment.candidate.lastName}`,
            status: assignment.candidate.status
          },
          assignment: {
            id: assignment._id,
            status: assignment.status,
            assignedTo: assignment.assignedTo,
            feedback: assignment.feedback
          },
          timestamp: assignment.reviewedAt,
          description: `Feedback submitted for ${assignment.candidate.referenceNumber} by ${assignment.assignedTo?.name || 'Unknown'}`
        });
      }
    });

    // Sort timeline by timestamp (newest first)
    timeline.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    res.json({ timeline: timeline.slice(0, 50) }); // Return last 50 events
  } catch (error) {
    console.error('Clusters timeline error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 