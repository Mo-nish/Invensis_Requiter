const jwt = require('jsonwebtoken');
const Admin = require('../models/Admin');

// Admin authentication middleware
const adminAuth = async (req, res, next) => {
  try {
    // Get token from header or cookie
    const token = req.header('Authorization')?.replace('Bearer ', '') || 
                  req.cookies?.admin_token;

    if (!token) {
      return res.status(401).json({ message: 'Access denied. No token provided.' });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.ADMIN_JWT_SECRET || 'admin-secret-key');
    
    // Check if admin exists and is active
    const admin = await Admin.findById(decoded.adminId);
    if (!admin || !admin.isActive) {
      return res.status(401).json({ message: 'Invalid token or admin not found.' });
    }

    // Add admin info to request
    req.adminId = admin._id;
    req.admin = admin;
    next();

  } catch (error) {
    console.error('Admin auth error:', error);
    res.status(401).json({ message: 'Invalid token.' });
  }
};

// Generate admin JWT token
const generateAdminToken = (admin) => {
  return jwt.sign(
    { adminId: admin._id, email: admin.email, role: 'admin' },
    process.env.ADMIN_JWT_SECRET || 'admin-secret-key',
    { expiresIn: '24h' }
  );
};

// Verify role assignment (helper function)
const verifyRoleAssignment = async (email, role) => {
  try {
    const RoleAssignment = require('../models/RoleAssignment');
    const assignment = await RoleAssignment.findOne({ 
      email: email.toLowerCase(), 
      role,
      isActive: true 
    });
    return assignment;
  } catch (error) {
    console.error('Role assignment verification error:', error);
    return null;
  }
};

module.exports = {
  adminAuth,
  generateAdminToken,
  verifyRoleAssignment
}; 