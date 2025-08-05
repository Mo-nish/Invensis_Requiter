import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  People,
  Assignment,
  Dashboard,
  TrendingUp,
  Email
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';

const DashboardOverview = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await axios.get('/api/admin/dashboard/overview');
      setOverview(response.data);
    } catch (error) {
      console.error('Fetch overview error:', error);
      toast.error('Failed to fetch dashboard overview');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!overview) {
    return (
      <Alert severity="error">
        Failed to load dashboard overview. Please try again.
      </Alert>
    );
  }

  const { roleStats, recentAssignments, systemStats } = overview;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard Overview
      </Typography>

      {/* System Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <People sx={{ mr: 2, color: 'primary.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Users
                  </Typography>
                  <Typography variant="h4">
                    {systemStats.totalUsers}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assignment sx={{ mr: 2, color: 'secondary.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Assignments
                  </Typography>
                  <Typography variant="h4">
                    {systemStats.totalAssignments}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Dashboard sx={{ mr: 2, color: 'success.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Candidates
                  </Typography>
                  <Typography variant="h4">
                    {systemStats.totalCandidates}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ mr: 2, color: 'info.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Roles
                  </Typography>
                  <Typography variant="h4">
                    {Object.keys(roleStats).length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Role Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {Object.entries(roleStats).map(([role, stats]) => (
          <Grid item xs={12} md={4} key={role}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {role} Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Total
                    </Typography>
                    <Typography variant="h5">
                      {stats.total}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Active
                    </Typography>
                    <Typography variant="h5" color="success.main">
                      {stats.active}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Pending
                    </Typography>
                    <Typography variant="h5" color="warning.main">
                      {stats.pending}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Registered
                    </Typography>
                    <Typography variant="h5" color="primary.main">
                      {stats.registered}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Assignments */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Role Assignments
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Invited By</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentAssignments.map((assignment) => (
                <TableRow key={assignment._id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Email sx={{ mr: 1, color: 'text.secondary' }} />
                      {assignment.email}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={assignment.role} size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={assignment.status}
                      color={assignment.status === 'active' ? 'success' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {assignment.invitedBy?.name || 'N/A'}
                  </TableCell>
                  <TableCell>
                    {new Date(assignment.invitedAt).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {recentAssignments.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              No recent role assignments
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default DashboardOverview; 