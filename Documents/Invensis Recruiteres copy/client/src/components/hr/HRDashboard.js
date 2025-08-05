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
import CreateCandidate from './CreateCandidate';
import CandidatesList from './CandidatesList';
import UpdatedList from './UpdatedList';
import DashboardHome from '../common/DashboardHome';
import axios from 'axios';

const HRDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Fetch candidates for dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/candidates');
        setDashboardData(response.data.candidates || []);
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
            Invensis Hiring Portal - HR Dashboard
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
            <Tab label="Create New Candidate Profile" />
            <Tab label="Candidates List" />
            <Tab label="Feedback" />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        {activeTab === 0 && (
          <DashboardHome 
            data={dashboardData} 
            title="HR Dashboard Overview" 
            loading={loading}
          />
        )}
        {activeTab === 1 && <CreateCandidate />}
        {activeTab === 2 && <CandidatesList />}
        {activeTab === 3 && <UpdatedList />}
      </Container>
    </Box>
  );
};

export default HRDashboard; 