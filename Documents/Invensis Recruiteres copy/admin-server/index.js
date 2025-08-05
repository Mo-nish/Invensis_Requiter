const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(cors({
  origin: ['http://localhost:3002', 'http://localhost:3000'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Connect to MongoDB (same database as main app)
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/invensis-recruiters', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('✅ Admin Server: Connected to MongoDB'))
.catch(err => console.error('❌ Admin Server: MongoDB connection error:', err));

// Import routes
const authRoutes = require('./routes/auth');
const roleRoutes = require('./routes/roles');
const dashboardRoutes = require('./routes/dashboard');

// Routes
app.use('/api/admin/auth', authRoutes);
app.use('/api/admin/roles', roleRoutes);
app.use('/api/admin/dashboard', dashboardRoutes);

// Health check
app.get('/api/admin/health', (req, res) => {
  res.json({ 
    message: 'Admin Server is running', 
    timestamp: new Date().toISOString() 
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

const PORT = process.env.ADMIN_PORT || 5002;

app.listen(PORT, () => {
  console.log(`🚀 Admin Server running on port ${PORT}`);
  console.log(`📧 Email Service: ${process.env.EMAIL_USER ? 'ENABLED' : 'DISABLED'}`);
}); 