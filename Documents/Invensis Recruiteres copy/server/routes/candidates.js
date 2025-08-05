const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { body, validationResult } = require('express-validator');
const Candidate = require('../models/Candidate');
const { auth, requireRole } = require('../middleware/auth');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.fieldname === 'image') {
      // Allow only image files
      if (file.mimetype.startsWith('image/')) {
        cb(null, true);
      } else {
        cb(new Error('Only image files are allowed for profile picture'));
      }
    } else if (file.fieldname === 'resume') {
      // Allow only PDF files
      if (file.mimetype === 'application/pdf') {
        cb(null, true);
      } else {
        cb(new Error('Only PDF files are allowed for resume'));
      }
    } else {
      cb(new Error('Invalid field name'));
    }
  }
});

// Create new candidate (HR only)
router.post('/', auth, requireRole(['HR']), upload.fields([
  { name: 'image', maxCount: 1 },
  { name: 'resume', maxCount: 1 }
]), [
  body('firstName').trim().isLength({ min: 2 }).withMessage('First name must be at least 2 characters long'),
  body('lastName').trim().isLength({ min: 2 }).withMessage('Last name must be at least 2 characters long'),
  body('phoneNumber').trim().isLength({ min: 10 }).withMessage('Phone number must be at least 10 characters long'),
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email'),
  body('gender').isIn(['Male', 'Female', 'Other']).withMessage('Gender must be Male, Female, or Other'),
  body('dateOfBirth').isISO8601().withMessage('Please provide a valid date of birth'),
  body('education').trim().notEmpty().withMessage('Education is required'),
  body('experience').trim().notEmpty().withMessage('Experience is required'),
  body('technicalTestRating').optional().isInt({ min: 1, max: 10 }).withMessage('Technical test rating must be between 1 and 10'),
  body('hrInterviewRating').optional().isInt({ min: 1, max: 10 }).withMessage('HR interview rating must be between 1 and 10'),
  body('hrReview').optional().trim()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    if (!req.files || !req.files.image || !req.files.resume) {
      return res.status(400).json({ message: 'Both image and resume are required' });
    }

    const {
      firstName,
      lastName,
      phoneNumber,
      email,
      gender,
      dateOfBirth,
      education,
      experience,
      technicalTestRating,
      hrInterviewRating,
      hrReview
    } = req.body;

    const candidate = new Candidate({
      firstName,
      lastName,
      phoneNumber,
      email,
      gender,
      dateOfBirth: new Date(dateOfBirth),
      education,
      experience,
      technicalTestRating: technicalTestRating ? parseInt(technicalTestRating) : undefined,
      hrInterviewRating: hrInterviewRating ? parseInt(hrInterviewRating) : undefined,
      hrReview,
      image: req.files.image[0].filename,
      resume: req.files.resume[0].filename,
      createdBy: req.user._id
    });

    await candidate.save();

    res.status(201).json({
      message: 'Candidate created successfully',
      candidate: {
        id: candidate._id,
        referenceNumber: candidate.referenceNumber,
        fullName: candidate.fullName,
        email: candidate.email,
        status: candidate.status,
        createdAt: candidate.createdAt
      }
    });
  } catch (error) {
    console.error('Create candidate error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get all candidates (HR can see all, Manager can see assigned)
router.get('/', auth, async (req, res) => {
  try {
    let candidates;
    
    if (req.user.designation === 'HR') {
      // HR can see all candidates
      candidates = await Candidate.find()
        .populate('createdBy', 'name email')
        .sort({ createdAt: -1 });
    } else {
      // Manager can only see assigned candidates
      const Assignment = require('../models/Assignment');
      const assignments = await Assignment.find({ assignedTo: req.user._id })
        .populate('candidate')
        .populate('assignedBy', 'name email');
      
      candidates = assignments.map(assignment => ({
        ...assignment.candidate.toObject(),
        assignment: {
          id: assignment._id,
          status: assignment.status,
          assignedAt: assignment.assignedAt,
          assignedBy: assignment.assignedBy
        }
      }));
    }

    res.json({ candidates });
  } catch (error) {
    console.error('Get candidates error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get candidate by ID
router.get('/:id', auth, async (req, res) => {
  try {
    const candidate = await Candidate.findById(req.params.id)
      .populate('createdBy', 'name email');

    if (!candidate) {
      return res.status(404).json({ message: 'Candidate not found' });
    }

    // Check if manager has access to this candidate
    if (req.user.designation === 'Manager') {
      const Assignment = require('../models/Assignment');
      const assignment = await Assignment.findOne({
        candidate: req.params.id,
        assignedTo: req.user._id
      });

      if (!assignment) {
        return res.status(403).json({ message: 'Access denied' });
      }
    }

    res.json({ candidate });
  } catch (error) {
    console.error('Get candidate error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update candidate (HR only)
router.put('/:id', auth, requireRole(['HR']), async (req, res) => {
  try {
    const candidate = await Candidate.findById(req.params.id);

    if (!candidate) {
      return res.status(404).json({ message: 'Candidate not found' });
    }

    // Only allow updates if candidate is not assigned
    if (candidate.status !== 'New') {
      return res.status(400).json({ message: 'Cannot update assigned candidate' });
    }

    const updates = req.body;
    Object.keys(updates).forEach(key => {
      if (key !== 'referenceNumber' && key !== 'createdBy' && key !== 'createdAt') {
        candidate[key] = updates[key];
      }
    });

    await candidate.save();

    res.json({
      message: 'Candidate updated successfully',
      candidate
    });
  } catch (error) {
    console.error('Update candidate error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete candidate (HR and Manager)
router.delete('/:id', auth, requireRole(['HR', 'Manager']), async (req, res) => {
  try {
    const candidate = await Candidate.findById(req.params.id);

    if (!candidate) {
      return res.status(404).json({ message: 'Candidate not found' });
    }

    // For managers, check if they have access to this candidate
    if (req.user.designation === 'Manager') {
      const Assignment = require('../models/Assignment');
      const assignment = await Assignment.findOne({
        candidate: req.params.id,
        assignedTo: req.user._id
      });

      if (!assignment) {
        return res.status(403).json({ message: 'Access denied' });
      }
    }

    // Delete associated assignments first
    const Assignment = require('../models/Assignment');
    await Assignment.deleteMany({ candidate: req.params.id });

    // Delete associated files
    if (candidate.image) {
      const imagePath = path.join(__dirname, '../../uploads', candidate.image);
      if (fs.existsSync(imagePath)) {
        fs.unlinkSync(imagePath);
      }
    }

    if (candidate.resume) {
      const resumePath = path.join(__dirname, '../../uploads', candidate.resume);
      if (fs.existsSync(resumePath)) {
        fs.unlinkSync(resumePath);
      }
    }

    await candidate.deleteOne();

    res.json({ message: 'Candidate deleted successfully' });
  } catch (error) {
    console.error('Delete candidate error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 