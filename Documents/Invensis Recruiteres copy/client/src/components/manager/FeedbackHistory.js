import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Chip,
  IconButton,
  Collapse,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Avatar
} from '@mui/material';
import {
  KeyboardArrowDown,
  KeyboardArrowUp,
  Visibility,
  Download,
  Delete,
  Star,
  RateReview
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';
import { format } from 'date-fns';
import FilterBar from '../common/FilterBar';

const FeedbackHistory = () => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
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
      // Filter for assignments with feedback submitted
      const reviewedAssignments = response.data.assignments.filter(
        assignment => assignment.feedbackSubmitted || 
                    assignment.status === 'Feedback Submitted' ||
                    ['Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR'].includes(assignment.status)
      );
      setAssignments(reviewedAssignments);
    } catch (error) {
      toast.error('Failed to fetch feedback history');
    } finally {
      setLoading(false);
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'Shortlisted':
        return 'success';
      case 'Rejected':
        return 'error';
      case 'On Hold':
        return 'info';
      case 'Interview Scheduled':
        return 'warning';
      case 'Reassigned to HR':
        return 'default';
      case 'Feedback Submitted':
        return 'success';
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

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
        Manager Feedback Summary
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

      <Paper elevation={3}>
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
                          <KeyboardArrowUp />
                        ) : (
                          <KeyboardArrowDown />
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
                          <Card variant="outlined">
                            <CardContent>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <Typography variant="h6" gutterBottom>
                                    Candidate Details
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Email:</strong> {assignment.candidate.email}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Phone:</strong> {assignment.candidate.phoneNumber}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Gender:</strong> {assignment.candidate.gender}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Age:</strong> {assignment.candidate.age} years
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Education:</strong> {assignment.candidate.education}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Experience:</strong> {assignment.candidate.experience}
                                  </Typography>
                                </Grid>
                                
                                {/* HR Ratings & Reviews Section */}
                                {(assignment.candidate.technicalTestRating || assignment.candidate.hrInterviewRating || assignment.candidate.hrReview) && (
                                  <Grid item xs={12}>
                                    <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.50', borderRadius: 1, border: '1px solid', borderColor: 'primary.200' }}>
                                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'primary.main' }}>
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
                                  <Typography variant="h6" gutterBottom>
                                    Manager Feedback Summary
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Assigned Date:</strong>{' '}
                                    {format(new Date(assignment.assignedAt), 'MMM dd, yyyy HH:mm')}
                                  </Typography>
                                  
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
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Feedback:</strong>
                                    </Typography>
                                  )}
                                  {assignment.feedback && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                                      {assignment.feedback}
                                    </Typography>
                                  )}
                                  
                                  {assignment.interviewNotes && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Interview Notes:</strong>
                                    </Typography>
                                  )}
                                  {assignment.interviewNotes && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2, p: 1, bgcolor: 'blue.50', borderRadius: 1 }}>
                                      {assignment.interviewNotes}
                                    </Typography>
                                  )}
                                  
                                  {assignment.managerComments && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Manager Comments:</strong>
                                    </Typography>
                                  )}
                                  {assignment.managerComments && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2, p: 1, bgcolor: 'green.50', borderRadius: 1 }}>
                                      {assignment.managerComments}
                                    </Typography>
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
              ? 'No feedback history found. Review some assigned candidates to see them here.'
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

export default FeedbackHistory; 