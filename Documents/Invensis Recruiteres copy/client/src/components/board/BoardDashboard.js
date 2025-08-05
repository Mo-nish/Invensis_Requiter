import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Tabs,
  Tab,
  Button,
  Collapse,
  IconButton as MuiIconButton,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Dashboard,
  People,
  Assignment,
  TrendingUp,
  Logout,
  Person,
  Visibility,
  Refresh,
  KeyboardArrowDown,
  KeyboardArrowUp,
  Star,
  RateReview,
  Schedule,
  AccessTime
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { format } from 'date-fns';

const BoardDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [candidates, setCandidates] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData(true); // Silent refresh
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async (silent = false) => {
    if (!silent) {
      setLoading(true);
    }
    
    try {
      // Fetch comprehensive board data
      const boardResponse = await axios.get('/api/board/candidates');
      const boardData = boardResponse.data;

      setCandidates(boardData.candidates);
      setAssignments(boardData.assignments);
      setLastUpdated(new Date());
      
      if (!silent) {
        toast.success('Dashboard data updated successfully');
      }
    } catch (error) {
      console.error('Fetch dashboard data error:', error);
      if (!silent) {
        toast.error('Failed to fetch dashboard data');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  const toggleRow = (candidateId) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(candidateId)) {
      newExpandedRows.delete(candidateId);
    } else {
      newExpandedRows.add(candidateId);
    }
    setExpandedRows(newExpandedRows);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'New':
        return 'default';
      case 'Assigned':
        return 'primary';
      case 'Under Review':
        return 'warning';
      case 'Shortlisted':
        return 'success';
      case 'Rejected':
        return 'error';
      case 'On Hold':
        return 'info';
      case 'Reassigned to HR':
        return 'default';
      default:
        return 'default';
    }
  };

  const getRatingColor = (rating) => {
    if (!rating) return 'default';
    if (rating >= 8) return 'success';
    if (rating >= 5) return 'warning';
    return 'error';
  };

  const calculateAverageRating = (technicalRating, hrRating) => {
    if (!technicalRating && !hrRating) return null;
    if (!technicalRating) return hrRating;
    if (!hrRating) return technicalRating;
    return ((technicalRating + hrRating) / 2).toFixed(1);
  };

  const getStats = () => {
    const totalCandidates = candidates.length;
    const totalAssignments = assignments.length;
    const shortlistedCount = candidates.filter(c => c.status === 'Shortlisted').length;
    const underReviewCount = candidates.filter(c => c.status === 'Under Review').length;
    const assignedCount = candidates.filter(c => c.status === 'Assigned').length;
    const rejectedCount = candidates.filter(c => c.status === 'Rejected').length;

    return {
      totalCandidates,
      totalAssignments,
      shortlistedCount,
      underReviewCount,
      assignedCount,
      rejectedCount
    };
  };

  const stats = getStats();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Dashboard sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Clusters Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" color="inherit">
              Welcome, {user?.name}
            </Typography>
            
            <Button
              color="inherit"
              startIcon={<Refresh />}
              onClick={handleRefresh}
              disabled={refreshing}
              sx={{ mr: 1 }}
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            
            <IconButton
              color="inherit"
              onClick={handleMenuOpen}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                <Person />
              </Avatar>
            </IconButton>
            
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <People sx={{ mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Candidates
                    </Typography>
                    <Typography variant="h4">
                      {stats.totalCandidates}
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
                      {stats.totalAssignments}
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
                  <TrendingUp sx={{ mr: 2, color: 'success.main' }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Shortlisted
                    </Typography>
                    <Typography variant="h4">
                      {stats.shortlistedCount}
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
                  <Visibility sx={{ mr: 2, color: 'info.main' }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Under Review
                    </Typography>
                    <Typography variant="h4">
                      {stats.underReviewCount}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Last Updated Info */}
        {lastUpdated && (
          <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccessTime fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              Last updated: {format(lastUpdated, 'HH:mm:ss')}
            </Typography>
          </Box>
        )}

        {/* Tabs */}
        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="Candidates Overview" />
            <Tab label="HR Feedback" />
            <Tab label="Manager Feedback" />
            <Tab label="Timeline" />
          </Tabs>

          {/* Tab Content */}
          {activeTab === 0 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                All Candidates
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ width: '50px' }}></TableCell>
                      <TableCell>Reference #</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Assignment</TableCell>
                      <TableCell>Created Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidates.map((candidate) => (
                      <React.Fragment key={candidate._id}>
                        <TableRow hover>
                          <TableCell>
                            <MuiIconButton size="small" onClick={() => toggleRow(candidate._id)}>
                              {expandedRows.has(candidate._id) ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                            </MuiIconButton>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {candidate.referenceNumber}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {candidate.firstName && candidate.lastName 
                              ? `${candidate.firstName} ${candidate.lastName}` 
                              : 'N/A'
                            }
                          </TableCell>
                          <TableCell>{candidate.email}</TableCell>
                          <TableCell>
                            <Chip
                              label={candidate.status}
                              color={getStatusColor(candidate.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {candidate.hasAssignment ? (
                              <Chip
                                label={candidate.assignmentStatus}
                                color={getStatusColor(candidate.assignmentStatus)}
                                size="small"
                                variant="outlined"
                              />
                            ) : (
                              <Chip label="Not Assigned" color="default" size="small" />
                            )}
                          </TableCell>
                          <TableCell>
                            {format(new Date(candidate.createdAt), 'MMM dd, yyyy')}
                          </TableCell>
                        </TableRow>
                        
                        <TableRow>
                          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
                            <Collapse in={expandedRows.has(candidate._id)} timeout="auto" unmountOnExit>
                              <Box sx={{ margin: 1 }}>
                                <Card variant="outlined">
                                  <CardContent>
                                    <Grid container spacing={2}>
                                      <Grid item xs={12} md={6}>
                                        <Typography variant="h6" gutterBottom>
                                          Candidate Details
                                        </Typography>
                                        <Typography variant="body2" sx={{ mb: 1 }}>
                                          <strong>Gender:</strong> {candidate.gender}
                                        </Typography>
                                        <Typography variant="body2" sx={{ mb: 1 }}>
                                          <strong>Age:</strong> {candidate.age} years
                                        </Typography>
                                        <Typography variant="body2" sx={{ mb: 1 }}>
                                          <strong>Education:</strong> {candidate.education}
                                        </Typography>
                                        <Typography variant="body2" sx={{ mb: 1 }}>
                                          <strong>Experience:</strong> {candidate.experience}
                                        </Typography>
                                        <Typography variant="body2" sx={{ mb: 1 }}>
                                          <strong>Phone:</strong> {candidate.phoneNumber}
                                        </Typography>
                                      </Grid>
                                      
                                      {candidate.hasAssignment && (
                                        <Grid item xs={12} md={6}>
                                          <Typography variant="h6" gutterBottom>
                                            Assignment Details
                                          </Typography>
                                          <Typography variant="body2" sx={{ mb: 1 }}>
                                            <strong>Assigned To:</strong> {candidate.assignedTo}
                                          </Typography>
                                          <Typography variant="body2" sx={{ mb: 1 }}>
                                            <strong>Assigned By:</strong> {candidate.assignedBy}
                                          </Typography>
                                          <Typography variant="body2" sx={{ mb: 1 }}>
                                            <strong>Assigned Date:</strong> {candidate.assignedAt ? format(new Date(candidate.assignedAt), 'MMM dd, yyyy') : 'N/A'}
                                          </Typography>
                                          {candidate.interviewDate && (
                                            <Typography variant="body2" sx={{ mb: 1 }}>
                                              <strong>Interview Date:</strong> {format(new Date(candidate.interviewDate), 'MMM dd, yyyy HH:mm')}
                                            </Typography>
                                          )}
                                        </Grid>
                                      )}
                                    </Grid>
                                  </CardContent>
                                </Card>
                              </Box>
                            </Collapse>
                          </TableCell>
                        </TableRow>
                      </React.Fragment>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {activeTab === 1 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                HR Feedback & Ratings
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Reference #</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Technical Rating</TableCell>
                      <TableCell>HR Interview Rating</TableCell>
                      <TableCell>Average Rating</TableCell>
                      <TableCell>HR Review</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidates.filter(c => c.technicalTestRating || c.hrInterviewRating || c.hrReview).map((candidate) => (
                      <TableRow key={candidate._id}>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {candidate.referenceNumber}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {candidate.firstName && candidate.lastName 
                            ? `${candidate.firstName} ${candidate.lastName}` 
                            : 'N/A'
                          }
                        </TableCell>
                        <TableCell>
                          {candidate.technicalTestRating ? (
                            <Chip
                              label={`${candidate.technicalTestRating}/10`}
                              color={getRatingColor(candidate.technicalTestRating)}
                              size="small"
                            />
                          ) : (
                            <Typography variant="body2" color="text.secondary">Not rated</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {candidate.hrInterviewRating ? (
                            <Chip
                              label={`${candidate.hrInterviewRating}/10`}
                              color={getRatingColor(candidate.hrInterviewRating)}
                              size="small"
                            />
                          ) : (
                            <Typography variant="body2" color="text.secondary">Not rated</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {(() => {
                            const avg = calculateAverageRating(candidate.technicalTestRating, candidate.hrInterviewRating);
                            return avg ? (
                              <Chip
                                label={`${avg}/10`}
                                color={getRatingColor(parseFloat(avg))}
                                size="small"
                                variant="outlined"
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">N/A</Typography>
                            );
                          })()}
                        </TableCell>
                        <TableCell>
                          {candidate.hrReview ? (
                            <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {candidate.hrReview}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">No review</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={candidate.status}
                            color={getStatusColor(candidate.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              {candidates.filter(c => c.technicalTestRating || c.hrInterviewRating || c.hrReview).length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary">
                    No HR feedback available
                  </Typography>
                </Box>
              )}
            </Box>
          )}

          {activeTab === 2 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Manager Feedback
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Reference #</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Manager</TableCell>
                      <TableCell>Assignment Status</TableCell>
                      <TableCell>Feedback</TableCell>
                      <TableCell>Comments</TableCell>
                      <TableCell>Interview Date</TableCell>
                      <TableCell>Reviewed At</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidates.filter(c => c.hasAssignment && (c.managerFeedback || c.managerComments)).map((candidate) => (
                      <TableRow key={candidate._id}>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {candidate.referenceNumber}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {candidate.firstName && candidate.lastName 
                            ? `${candidate.firstName} ${candidate.lastName}` 
                            : 'N/A'
                          }
                        </TableCell>
                        <TableCell>{candidate.assignedTo}</TableCell>
                        <TableCell>
                          <Chip
                            label={candidate.assignmentStatus}
                            color={getStatusColor(candidate.assignmentStatus)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {candidate.managerFeedback ? (
                            <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {candidate.managerFeedback}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">No feedback</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {candidate.managerComments ? (
                            <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {candidate.managerComments}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">No comments</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {candidate.interviewDate ? format(new Date(candidate.interviewDate), 'MMM dd, yyyy') : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {candidate.reviewedAt ? format(new Date(candidate.reviewedAt), 'MMM dd, yyyy') : 'N/A'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              {candidates.filter(c => c.hasAssignment && (c.managerFeedback || c.managerComments)).length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary">
                    No manager feedback available
                  </Typography>
                </Box>
              )}
            </Box>
          )}

          {activeTab === 3 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Timeline - Recent Activities
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Reference #</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Activity</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidates
                      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
                      .slice(0, 20)
                      .map((candidate) => (
                        <TableRow key={candidate._id}>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {candidate.referenceNumber}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {candidate.firstName && candidate.lastName 
                              ? `${candidate.firstName} ${candidate.lastName}` 
                              : 'N/A'
                            }
                          </TableCell>
                          <TableCell>
                            {candidate.hasAssignment ? 'Assigned to Manager' : 'Candidate Created'}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={candidate.status}
                              color={getStatusColor(candidate.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {format(new Date(candidate.createdAt), 'MMM dd, yyyy HH:mm')}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default BoardDashboard; 