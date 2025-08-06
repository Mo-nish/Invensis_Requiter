const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables from root directory
dotenv.config({ path: '../../.env' });

const app = express();

// CORS configuration for production
app.use(cors({
  origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : [
    'http://localhost:3001',  // Admin client (actual port)
    'http://localhost:3002',  // Admin client (intended port)
    'http://localhost:3000',  // Main app
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/invensis-recruiters')
  .then(() => {
    console.log('✅ Admin Server: Connected to MongoDB');
  })
  .catch((error) => {
    console.error('❌ MongoDB connection error:', error);
  });

// Import routes
const authRoutes = require('./routes/auth');
const rolesRoutes = require('./routes/roles');
const dashboardRoutes = require('./routes/dashboard');

// Use routes
app.use('/api/admin/auth', authRoutes);
app.use('/api/admin/roles', rolesRoutes);
app.use('/api/admin/dashboard', dashboardRoutes);

// Health check endpoint
app.get('/api/admin/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Admin server is running',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'Invensis Admin Portal API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/api/admin/health',
      auth: '/api/admin/auth',
      roles: '/api/admin/roles',
      dashboard: '/api/admin/dashboard'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Admin Server Error:', err);
  res.status(500).json({ 
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ message: 'Admin API endpoint not found' });
});

const PORT = process.env.PORT || 5002;

app.listen(PORT, () => {
  console.log(`🚀 Admin Server running on port ${PORT}`);
  console.log(`📧 Email Service: ${process.env.EMAIL_USER ? 'ENABLED' : 'DISABLED'}`);
}); 