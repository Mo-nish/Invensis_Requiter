const jwt = require('jsonwebtoken');
const Admin = require('../models/Admin');

const JWT_SECRET = process.env.ADMIN_JWT_SECRET || 'admin-super-secret-jwt-key';

// Middleware to verify admin token
const adminAuth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '') || 
                  req.cookies?.admin_token;

    if (!token) {
      return res.status(401).json({ 
        message: 'Access denied. No admin token provided.',
        redirectTo: '/admin/login'
      });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    
    // Check if admin exists and is active
    const admin = await Admin.findById(decoded.adminId);
    if (!admin || !admin.isActive || admin.role !== 'admin') {
      return res.status(401).json({ 
        message: 'Invalid admin token.',
        redirectTo: '/admin/login'
      });
    }

    req.admin = admin;
    next();
  } catch (error) {
    console.error('Admin Auth Error:', error);
    return res.status(401).json({ 
      message: 'Invalid admin token.',
      redirectTo: '/admin/login'
    });
  }
};

// Generate admin JWT token
const generateAdminToken = (adminId) => {
  return jwt.sign(
    { adminId, type: 'admin' },
    JWT_SECRET,
    { expiresIn: '24h' }
  );
};

// Verify role assignment (for user registration)
const verifyRoleAssignment = async (email, role) => {
  const RoleAssignment = require('../models/RoleAssignment');
  
  const assignment = await RoleAssignment.findOne({ 
    email: email.toLowerCase(), 
    role,
    isActive: true 
  });
  
  return assignment;
};

module.exports = {
  adminAuth,
  generateAdminToken,
  verifyRoleAssignment,
  JWT_SECRET
}; 