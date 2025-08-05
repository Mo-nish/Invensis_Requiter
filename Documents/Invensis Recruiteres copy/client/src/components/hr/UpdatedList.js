import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  IconButton,
  Collapse,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Sort as SortIcon,
  ViewList as ViewListIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  Work as WorkIcon,
  School as SchoolIcon,
  Star as StarIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Visibility,
  Download,
  Delete,
  KeyboardArrowDown,
  KeyboardArrowUp,
  Schedule,
  RateReview,
  Email,
  Phone,
  School,
  Work,
  Star,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';
import { format } from 'date-fns';
import FilterBar from '../common/FilterBar';

const UpdatedList = () => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [searchValue, setSearchValue] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await axios.get('/api/assignments');
      // Filter assignments that have feedback (status other than 'Assigned')
      const assignmentsWithFeedback = response.data.assignments.filter(
        assignment => assignment.status !== 'Assigned' && assignment.feedback
      );
      setAssignments(assignmentsWithFeedback);
    } catch (error) {
      console.error('Fetch assignments error:', error);
      toast.error('Failed to fetch updated candidates');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Under Review':
        return 'warning';
      case 'Interview Scheduled':
        return 'info';
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

  const calculateAverageRating = (technicalRating, interviewRating) => {
    if (!technicalRating && !interviewRating) return null;
    if (!technicalRating) return interviewRating;
    if (!interviewRating) return technicalRating;
    return ((technicalRating + interviewRating) / 2).toFixed(1);
  };

  const handleViewResume = (resumeUrl) => {
    window.open(`http://localhost:5001/uploads/${resumeUrl}`, '_blank');
  };

  const handleViewImage = (imageUrl) => {
    window.open(`http://localhost:5001/uploads/${imageUrl}`, '_blank');
  };

  const handleDeleteClick = (candidate) => {
    setCandidateToDelete(candidate);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!candidateToDelete) return;

    setDeleteLoading(true);
    try {
      await axios.delete(`/api/candidates/${candidateToDelete._id}`);
      toast.success('Candidate deleted successfully!');
      setDeleteDialogOpen(false);
      setCandidateToDelete(null);
      fetchAssignments(); // Refresh the list
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to delete candidate';
      toast.error(message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const toggleRow = (assignmentId) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(assignmentId)) {
      newExpandedRows.delete(assignmentId);
    } else {
      newExpandedRows.add(assignmentId);
    }
    setExpandedRows(newExpandedRows);
  };

  // Filter assignments based on search and filters
  const filteredAssignments = assignments.filter(assignment => {
    // Search filter
    const searchLower = searchValue.toLowerCase();
    const matchesSearch = !searchValue || 
      assignment.candidate.referenceNumber.toLowerCase().includes(searchLower) ||
      (assignment.candidate.firstName && assignment.candidate.firstName.toLowerCase().includes(searchLower)) ||
      (assignment.candidate.lastName && assignment.candidate.lastName.toLowerCase().includes(searchLower)) ||
      assignment.candidate.email.toLowerCase().includes(searchLower);

    // Status filter
    const matchesStatus = statusFilter === 'all' || assignment.status === statusFilter;

    // Date filter
    let matchesDate = true;
    if (dateFrom || dateTo) {
      const assignmentDate = new Date(assignment.assignedAt);
      if (dateFrom) {
        const fromDate = new Date(dateFrom);
        matchesDate = matchesDate && assignmentDate >= fromDate;
      }
      if (dateTo) {
        const toDate = new Date(dateTo);
        toDate.setHours(23, 59, 59, 999); // End of day
        matchesDate = matchesDate && assignmentDate <= toDate;
      }
    }

    return matchesSearch && matchesStatus && matchesDate;
  });

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
        Feedback from Managers
      </Typography>

      {/* Filter Bar */}
      <FilterBar
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        dateFrom={dateFrom}
        onDateFromChange={setDateFrom}
        dateTo={dateTo}
        onDateToChange={setDateTo}
      />

      <Paper elevation={3} sx={{ borderRadius: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ width: '50px', fontWeight: 'bold' }}></TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '150px' }}>Reference #</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '200px' }}>Email</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '100px', textAlign: 'center' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Review Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px', textAlign: 'center' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAssignments.map((assignment) => (
                <React.Fragment key={assignment._id}>
                  <TableRow 
                    hover 
                    sx={{ cursor: 'pointer' }}
                    onClick={() => toggleRow(assignment._id)}
                  >
                    <TableCell sx={{ width: '50px' }}>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleRow(assignment._id);
                        }}
                      >
                        {expandedRows.has(assignment._id) ? (
                          <ExpandLessIcon />
                        ) : (
                          <ExpandMoreIcon />
                        )}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar
                          src={`http://localhost:5001/uploads/${assignment.candidate.image}`}
                          sx={{ width: 40, height: 40, mr: 2 }}
                        />
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {assignment.candidate.referenceNumber}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        {assignment.candidate.firstName && assignment.candidate.lastName ? `${assignment.candidate.firstName} ${assignment.candidate.lastName}` : assignment.candidate.fullName || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>{assignment.candidate.email}</TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Chip
                        label={assignment.status}
                        color={getStatusColor(assignment.status)}
                        size="small"
                        sx={{
                          backgroundColor: assignment.status === 'Shortlisted' ? '#4caf50' : undefined,
                          color: assignment.status === 'Shortlisted' ? 'white' : undefined
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      {assignment.reviewedAt
                        ? format(new Date(assignment.reviewedAt), 'MMM dd, yyyy')
                        : 'Not reviewed yet'
                      }
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                        <Tooltip title="View Image">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewImage(assignment.candidate.image);
                            }}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Download Resume">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewResume(assignment.candidate.resume);
                            }}
                          >
                            <Download />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Delete Candidate">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteClick(assignment.candidate);
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                  
                  <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
                      <Collapse in={expandedRows.has(assignment._id)} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                          <Card variant="outlined" sx={{ borderRadius: 2 }}>
                            <CardContent>
                              <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                    Candidate Details
                                  </Typography>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Email sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body2">
                                      <strong>Email:</strong> {assignment.candidate.email}
                                    </Typography>
                                  </Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Phone sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body2">
                                      <strong>Phone:</strong> {assignment.candidate.phoneNumber}
                                    </Typography>
                                  </Box>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Gender:</strong> {assignment.candidate.gender}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Age:</strong> {assignment.candidate.age} years
                                  </Typography>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <School sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body2">
                                      <strong>Education:</strong> {assignment.candidate.education}
                                    </Typography>
                                  </Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Work sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body2">
                                      <strong>Experience:</strong> {assignment.candidate.experience}
                                    </Typography>
                                  </Box>
                                </Grid>
                                
                                {/* HR Ratings & Reviews Section */}
                                {(assignment.candidate.technicalTestRating || assignment.candidate.hrInterviewRating || assignment.candidate.hrReview) && (
                                  <Grid item xs={12}>
                                    <Box sx={{ mt: 2, p: 2, bgcolor: 'success.50', borderRadius: 1, border: '1px solid', borderColor: 'success.200' }}>
                                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'success.main' }}>
                                        <RateReview />
                                        HR Ratings & Review
                                      </Typography>
                                      
                                      <Grid container spacing={2}>
                                        <Grid item xs={12} md={6}>
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                            <Star color="primary" />
                                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                              Technical Test Rating:
                                            </Typography>
                                            {assignment.candidate.technicalTestRating ? (
                                              <Chip
                                                label={`${assignment.candidate.technicalTestRating}/10`}
                                                color={getRatingColor(assignment.candidate.technicalTestRating)}
                                                size="small"
                                              />
                                            ) : (
                                              <Typography variant="body2" color="text.secondary">
                                                Not rated
                                              </Typography>
                                            )}
                                          </Box>
                                          
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                            <Star color="primary" />
                                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                              HR Interview Rating:
                                            </Typography>
                                            {assignment.candidate.hrInterviewRating ? (
                                              <Chip
                                                label={`${assignment.candidate.hrInterviewRating}/10`}
                                                color={getRatingColor(assignment.candidate.hrInterviewRating)}
                                                size="small"
                                              />
                                            ) : (
                                              <Typography variant="body2" color="text.secondary">
                                                Not rated
                                              </Typography>
                                            )}
                                          </Box>
                                          
                                          {assignment.candidate.technicalTestRating && assignment.candidate.hrInterviewRating && (
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                              <Star color="success" />
                                              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                                Average Rating:
                                              </Typography>
                                              <Chip
                                                label={`${calculateAverageRating(assignment.candidate.technicalTestRating, assignment.candidate.hrInterviewRating)}/10`}
                                                color={getRatingColor(calculateAverageRating(assignment.candidate.technicalTestRating, assignment.candidate.hrInterviewRating))}
                                                size="small"
                                              />
                                            </Box>
                                          )}
                                        </Grid>
                                        
                                        <Grid item xs={12} md={6}>
                                          {assignment.candidate.hrReview && (
                                            <Box>
                                              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                                HR Review Notes:
                                              </Typography>
                                              <Typography variant="body2" sx={{ 
                                                p: 1.5, 
                                                bgcolor: 'background.paper', 
                                                borderRadius: 1,
                                                border: '1px solid',
                                                borderColor: 'grey.300',
                                                fontStyle: 'italic',
                                                fontSize: '0.875rem'
                                              }}>
                                                {assignment.candidate.hrReview}
                                              </Typography>
                                            </Box>
                                          )}
                                        </Grid>
                                      </Grid>
                                    </Box>
                                  </Grid>
                                )}
                                
                                <Grid item xs={12} md={6}>
                                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                    Manager Feedback Summary
                                  </Typography>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Schedule sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="body2">
                                      <strong>Assigned Date:</strong>{' '}
                                      {format(new Date(assignment.assignedAt), 'MMM dd, yyyy HH:mm')}
                                    </Typography>
                                  </Box>
                                  
                                  {assignment.reviewedAt && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Reviewed Date:</strong>{' '}
                                      {format(new Date(assignment.reviewedAt), 'MMM dd, yyyy HH:mm')}
                                    </Typography>
                                  )}
                                  
                                  {assignment.interviewDate && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Interview Date:</strong>{' '}
                                      {format(new Date(assignment.interviewDate), 'MMM dd, yyyy HH:mm')}
                                    </Typography>
                                  )}
                                  
                                  {assignment.feedback && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                        Feedback:
                                      </Typography>
                                      <Typography variant="body2" sx={{ 
                                        p: 2, 
                                        bgcolor: 'grey.50', 
                                        borderRadius: 1,
                                        border: '1px solid',
                                        borderColor: 'grey.200',
                                        fontStyle: 'italic'
                                      }}>
                                        {assignment.feedback}
                                      </Typography>
                                    </Box>
                                  )}
                                  
                                  {assignment.interviewNotes && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                        Interview Notes:
                                      </Typography>
                                      <Typography variant="body2" sx={{ 
                                        p: 2, 
                                        bgcolor: 'blue.50', 
                                        borderRadius: 1,
                                        border: '1px solid',
                                        borderColor: 'blue.200'
                                      }}>
                                        {assignment.interviewNotes}
                                      </Typography>
                                    </Box>
                                  )}
                                  
                                  {assignment.managerComments && (
                                    <Box sx={{ mb: 2 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                        Manager Comments:
                                      </Typography>
                                      <Typography variant="body2" sx={{ 
                                        p: 2, 
                                        bgcolor: 'green.50', 
                                        borderRadius: 1,
                                        border: '1px solid',
                                        borderColor: 'green.200'
                                      }}>
                                        {assignment.managerComments}
                                      </Typography>
                                    </Box>
                                  )}
                                </Grid>
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
      </Paper>

      {filteredAssignments.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            {assignments.length === 0 
              ? 'No candidates with feedback yet.'
              : 'No candidates match the current filters. Try adjusting your search criteria.'
            }
          </Typography>
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Delete Candidate</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body1" gutterBottom>
              Are you sure you want to delete this candidate?
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Name:</strong> {candidateToDelete?.firstName && candidateToDelete?.lastName ? `${candidateToDelete.firstName} ${candidateToDelete.lastName}` : candidateToDelete?.fullName || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Reference:</strong> {candidateToDelete?.referenceNumber}
            </Typography>
            <Typography variant="body2" color="error" sx={{ mt: 2 }}>
              This action cannot be undone. All associated data and feedback will be permanently deleted.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            disabled={deleteLoading}
          >
            {deleteLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UpdatedList; 