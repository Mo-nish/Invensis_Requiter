import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import { Logout } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import AssignedCandidates from './AssignedCandidates';
import FeedbackHistory from './FeedbackHistory';
import DashboardHome from '../common/DashboardHome';
import axios from 'axios';

const ManagerDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Callback function to handle feedback submission
  const handleFeedbackSubmitted = () => {
    // Switch to Feedback tab after a short delay to show the success message
    setTimeout(() => {
      setActiveTab(2);
    }, 1500);
  };

  // Fetch assignments for dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/assignments');
        setDashboardData(response.data.assignments || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setDashboardData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    logout();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Invensis Hiring Portal - Manager Dashboard
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Welcome, {user?.name}
          </Typography>
          <Button 
            color="inherit" 
            onClick={handleLogout}
            startIcon={<Logout />}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="Home" />
            <Tab label="Assigned Candidates" />
            <Tab label="Feedback" />
          </Tabs>

          {/* Tab Content */}
          {activeTab === 0 && (
            <DashboardHome 
              data={dashboardData} 
              title="Manager Dashboard Overview" 
              loading={loading}
            />
          )}
          {activeTab === 1 && <AssignedCandidates onFeedbackSubmitted={handleFeedbackSubmitted} />}
          {activeTab === 2 && <FeedbackHistory />}
        </Paper>
      </Container>
    </Box>
  );
};

export default ManagerDashboard; 