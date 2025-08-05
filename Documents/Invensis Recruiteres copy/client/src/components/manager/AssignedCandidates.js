import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  IconButton,
  Tooltip,
  Badge,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Collapse
} from '@mui/material';
import {
  Schedule,
  Visibility,
  Download,
  Delete,
  KeyboardArrowDown,
  KeyboardArrowUp,
  Star,
  RateReview
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';
import { format } from 'date-fns';
import FilterBar from '../common/FilterBar';

const AssignedCandidates = ({ onFeedbackSubmitted }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [feedbackForm, setFeedbackForm] = useState({
    status: '',
    feedback: '',
    interviewDate: '',
    interviewNotes: '',
    managerComments: ''
  });
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [searchValue, setSearchValue] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [removingAssignment, setRemovingAssignment] = useState(null);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      console.log('Fetching assignments with token:', localStorage.getItem('token'));
      const response = await axios.get('/api/assignments');
      console.log('Assignments response:', response.data);
      
      // Filter out assignments where feedback has been submitted
      const activeAssignments = response.data.assignments.filter(
        assignment => !assignment.feedbackSubmitted && assignment.status !== 'Feedback Submitted'
      );
      
      setAssignments(activeAssignments);
    } catch (error) {
      console.error('Fetch assignments error:', error);
      toast.error('Failed to fetch assignments');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackClick = (assignment) => {
    setSelectedAssignment(assignment);
    
    // Set a valid default status if current status is "Assigned"
    let defaultStatus = assignment.status;
    if (defaultStatus === 'Assigned') {
      defaultStatus = 'Under Review'; // Set a valid default status
    }
    
    setFeedbackForm({
      status: defaultStatus,
      feedback: assignment.feedback || '',
      interviewDate: assignment.interviewDate ? format(new Date(assignment.interviewDate), "yyyy-MM-dd'T'HH:mm") : '',
      interviewNotes: assignment.interviewNotes || '',
      managerComments: assignment.managerComments || ''
    });
    setFeedbackDialogOpen(true);
  };

  const handleFeedbackSubmit = async () => {
    if (!feedbackForm.status) {
      toast.error('Please select a status');
      return;
    }

    setFeedbackLoading(true);
    try {
      console.log('Submitting feedback for assignment:', selectedAssignment._id);
      console.log('Feedback data:', feedbackForm);
      console.log('Auth token:', localStorage.getItem('token'));
      
      const response = await axios.put(`/api/assignments/${selectedAssignment._id}`, feedbackForm);
      
      console.log('Feedback submission successful:', response.data);
      toast.success('Feedback submitted successfully! The candidate will be moved to the Feedback tab.');
      setFeedbackDialogOpen(false);
      
      // Add smooth transition by marking the assignment for removal
      setRemovingAssignment(selectedAssignment._id);
      
      // Remove the assignment from the list after a short delay
      setTimeout(() => {
        setAssignments(prev => prev.filter(a => a._id !== selectedAssignment._id));
        setRemovingAssignment(null);
      }, 500);
      
      // Call the callback to notify parent component
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
    } catch (error) {
      console.error('Feedback submission error:', error);
      console.error('Error response:', error.response);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      
      // Show specific validation error if available
      let message = 'Failed to submit feedback';
      if (error.response?.data?.errors && error.response.data.errors.length > 0) {
        message = error.response.data.errors[0].msg || message;
      } else if (error.response?.data?.message) {
        message = error.response.data.message;
      }
      
      toast.error(message);
    } finally {
      setFeedbackLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Assigned':
        return 'default';
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

  const isNewAssignment = (assignment) => {
    const assignedDate = new Date(assignment.assignedAt);
    const now = new Date();
    const diffTime = Math.abs(now - assignedDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 3;
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
  const filteredAssignments = (assignments || []).filter(assignment => {
    // Search filter
    const searchLower = searchValue.toLowerCase();
    const matchesSearch = !searchValue || 
      assignment.candidate?.referenceNumber?.toLowerCase().includes(searchLower) ||
      (assignment.candidate.firstName && assignment.candidate.firstName.toLowerCase().includes(searchLower)) ||
      (assignment.candidate.lastName && assignment.candidate.lastName.toLowerCase().includes(searchLower)) ||
      assignment.candidate?.email?.toLowerCase().includes(searchLower);

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
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
        Assigned Candidates
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
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Assigned Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px', textAlign: 'center' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAssignments.map((assignment) => (
                <React.Fragment key={assignment._id}>
                  <TableRow 
                    hover 
                    sx={{ 
                      cursor: 'pointer',
                      opacity: removingAssignment === assignment._id ? 0.5 : 1,
                      transition: 'opacity 0.5s ease-out'
                    }}
                    onClick={() => toggleRow(assignment._id)}
                  >
                    <TableCell sx={{ width: '50px' }}>
                      <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleRow(assignment._id); }}>
                        {expandedRows.has(assignment._id) ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Badge
                          badgeContent={isNewAssignment(assignment) ? 'NEW' : ''}
                          color="error"
                          sx={{ mr: 2 }}
                        >
                          <Avatar
                            src={`http://localhost:5001/uploads/${assignment.candidate?.image || ''}`}
                            sx={{ width: 40, height: 40 }}
                          />
                        </Badge>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {assignment.candidate?.referenceNumber || 'N/A'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        {assignment.candidate?.firstName && assignment.candidate?.lastName ? `${assignment.candidate.firstName} ${assignment.candidate.lastName}` : assignment.candidate?.fullName || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>{assignment.candidate?.email || 'N/A'}</TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
                        <Chip
                          label={assignment.status || 'N/A'}
                          color={getStatusColor(assignment.status)}
                          size="small"
                        />
                        {assignment.feedbackSubmitted && (
                          <Chip
                            label="Feedback Submitted"
                            color="success"
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.7rem' }}
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {assignment.assignedAt ? format(new Date(assignment.assignedAt), 'MMM dd, yyyy') : 'N/A'}
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                        <Tooltip title="View Image">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleViewImage(assignment.candidate?.image);
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
                              handleViewResume(assignment.candidate?.resume);
                            }}
                          >
                            <Download />
                          </IconButton>
                        </Tooltip>
                        
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<Schedule />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleFeedbackClick(assignment);
                          }}
                        >
                          Review
                        </Button>
                        
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
                                    Assignment Details
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    <strong>Assigned Date:</strong>{' '}
                                    {format(new Date(assignment.assignedAt), 'MMM dd, yyyy HH:mm')}
                                  </Typography>
                                  
                                  {assignment.feedback && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Previous Feedback:</strong>
                                    </Typography>
                                  )}
                                  {assignment.feedback && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2 }}>
                                      {assignment.feedback}
                                    </Typography>
                                  )}
                                  
                                  {assignment.interviewNotes && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Interview Notes:</strong>
                                    </Typography>
                                  )}
                                  {assignment.interviewNotes && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2 }}>
                                      {assignment.interviewNotes}
                                    </Typography>
                                  )}
                                  
                                  {assignment.managerComments && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Manager Comments:</strong>
                                    </Typography>
                                  )}
                                  {assignment.managerComments && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1, ml: 2 }}>
                                      {assignment.managerComments}
                                    </Typography>
                                  )}
                                  
                                  {assignment.interviewDate && (
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                      <strong>Interview Date:</strong>{' '}
                                      {format(new Date(assignment.interviewDate), 'MMM dd, yyyy HH:mm')}
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
              ? 'No candidates assigned to you yet.'
              : 'No candidates match the current filters. Try adjusting your search criteria.'
            }
          </Typography>
        </Box>
      )}

      {/* Feedback Dialog */}
      <Dialog open={feedbackDialogOpen} onClose={() => setFeedbackDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Review Candidate</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="h6" gutterBottom>
              {selectedAssignment?.candidate?.firstName && selectedAssignment?.candidate?.lastName ? `${selectedAssignment.candidate.firstName} ${selectedAssignment.candidate.lastName}` : selectedAssignment?.candidate?.fullName || 'N/A'} - {selectedAssignment?.candidate?.referenceNumber}
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={feedbackForm.status}
                    label="Status"
                    onChange={(e) => setFeedbackForm(prev => ({ ...prev, status: e.target.value }))}
                  >
                    <MenuItem value="Under Review">Under Review</MenuItem>
                    <MenuItem value="Interview Scheduled">Interview Scheduled</MenuItem>
                    <MenuItem value="Shortlisted">Shortlisted</MenuItem>
                    <MenuItem value="Rejected">Rejected</MenuItem>
                    <MenuItem value="On Hold">On Hold</MenuItem>
                    <MenuItem value="Reassigned to HR">Reassigned to HR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Interview Date (Optional)"
                  type="datetime-local"
                  value={feedbackForm.interviewDate}
                  onChange={(e) => setFeedbackForm(prev => ({ ...prev, interviewDate: e.target.value }))}
                  margin="normal"
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Feedback"
                  multiline
                  rows={3}
                  value={feedbackForm.feedback}
                  onChange={(e) => setFeedbackForm(prev => ({ ...prev, feedback: e.target.value }))}
                  margin="normal"
                  placeholder="Provide detailed feedback about the candidate..."
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Interview Notes (Optional)"
                  multiline
                  rows={2}
                  value={feedbackForm.interviewNotes}
                  onChange={(e) => setFeedbackForm(prev => ({ ...prev, interviewNotes: e.target.value }))}
                  margin="normal"
                  placeholder="Notes from the interview..."
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Manager Comments (Optional)"
                  multiline
                  rows={2}
                  value={feedbackForm.managerComments}
                  onChange={(e) => setFeedbackForm(prev => ({ ...prev, managerComments: e.target.value }))}
                  margin="normal"
                  placeholder="Additional comments for HR..."
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleFeedbackSubmit}
            variant="contained"
            disabled={feedbackLoading || !feedbackForm.status}
          >
            {feedbackLoading ? <CircularProgress size={20} /> : 'Submit Feedback'}
          </Button>
        </DialogActions>
      </Dialog>

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

export default AssignedCandidates; 