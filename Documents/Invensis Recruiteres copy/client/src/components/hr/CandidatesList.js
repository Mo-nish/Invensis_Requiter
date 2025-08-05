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
  Button,
  Typography,
  Box,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Assignment,
  Visibility,
  Download,
  Delete,
  Star
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';
import { format } from 'date-fns';
import FilterBar from '../common/FilterBar';

const CandidatesList = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [assignForm, setAssignForm] = useState({
    managerEmail: '',
    managerName: '',
    scheduleDate: ''
  });
  const [assignLoading, setAssignLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get('/api/candidates');
      setCandidates(response.data.candidates);
    } catch (error) {
      toast.error('Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignClick = (candidate) => {
    setSelectedCandidate(candidate);
    setAssignForm({
      managerEmail: '',
      managerName: '',
      scheduleDate: ''
    });
    setAssignDialogOpen(true);
  };

  const handleAssignSubmit = async () => {
    if (!assignForm.managerEmail) {
      toast.error('Please enter manager email');
      return;
    }

    setAssignLoading(true);
    try {
      const response = await axios.post('/api/assignments', {
        candidateId: selectedCandidate._id,
        managerEmail: assignForm.managerEmail,
        managerName: assignForm.managerName,
        scheduleDate: assignForm.scheduleDate || null
      });

      // Check email status and show appropriate message
      if (response.data.emailSent) {
        toast.success('Candidate assigned successfully! Email notification sent to manager.');
      } else {
        toast.success('Candidate assigned successfully!');
        toast.warning(`Email notification failed: ${response.data.emailMessage}`);
      }
      
      setAssignDialogOpen(false);
      fetchCandidates(); // Refresh the list
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to assign candidate';
      toast.error(message);
    } finally {
      setAssignLoading(false);
    }
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
      fetchCandidates(); // Refresh the list
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to delete candidate';
      toast.error(message);
    } finally {
      setDeleteLoading(false);
    }
  };

  // Filter candidates based on search and filters
  const filteredCandidates = candidates.filter(candidate => {
    // Search filter
    const searchLower = searchValue.toLowerCase();
    const matchesSearch = !searchValue || 
      candidate.referenceNumber.toLowerCase().includes(searchLower) ||
      (candidate.firstName && candidate.firstName.toLowerCase().includes(searchLower)) ||
      (candidate.lastName && candidate.lastName.toLowerCase().includes(searchLower)) ||
      candidate.email.toLowerCase().includes(searchLower);

    // Status filter
    const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter;

    // Date filter
    let matchesDate = true;
    if (dateFrom || dateTo) {
      const candidateDate = new Date(candidate.createdAt);
      if (dateFrom) {
        const fromDate = new Date(dateFrom);
        matchesDate = matchesDate && candidateDate >= fromDate;
      }
      if (dateTo) {
        const toDate = new Date(dateTo);
        toDate.setHours(23, 59, 59, 999); // End of day
        matchesDate = matchesDate && candidateDate <= toDate;
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
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
          Candidates List
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

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '150px' }}>Reference #</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '200px' }}>Email</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Phone</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px', textAlign: 'center' }}>HR Ratings</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '100px', textAlign: 'center' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Created Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold', minWidth: '120px', textAlign: 'center' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCandidates.map((candidate) => (
                <TableRow key={candidate._id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {candidate.referenceNumber}
                    </Typography>
                  </TableCell>
                  <TableCell>{candidate.firstName && candidate.lastName ? `${candidate.firstName} ${candidate.lastName}` : candidate.fullName || 'N/A'}</TableCell>
                  <TableCell>{candidate.email}</TableCell>
                  <TableCell>{candidate.phoneNumber}</TableCell>
                  <TableCell sx={{ textAlign: 'center' }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, alignItems: 'center' }}>
                      {candidate.technicalTestRating && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Star sx={{ fontSize: 14, color: 'primary.main' }} />
                          <Chip
                            label={`T: ${candidate.technicalTestRating}/10`}
                            color={getRatingColor(candidate.technicalTestRating)}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      )}
                      {candidate.hrInterviewRating && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Star sx={{ fontSize: 14, color: 'primary.main' }} />
                          <Chip
                            label={`I: ${candidate.hrInterviewRating}/10`}
                            color={getRatingColor(candidate.hrInterviewRating)}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      )}
                      {candidate.technicalTestRating && candidate.hrInterviewRating && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Star sx={{ fontSize: 14, color: 'success.main' }} />
                          <Chip
                            label={`Avg: ${calculateAverageRating(candidate.technicalTestRating, candidate.hrInterviewRating)}/10`}
                            color={getRatingColor(calculateAverageRating(candidate.technicalTestRating, candidate.hrInterviewRating))}
                            size="small"
                          />
                        </Box>
                      )}
                      {!candidate.technicalTestRating && !candidate.hrInterviewRating && (
                        <Typography variant="caption" color="text.secondary">
                          No ratings
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ textAlign: 'center' }}>
                    <Chip
                      label={candidate.status}
                      color={getStatusColor(candidate.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {format(new Date(candidate.createdAt), 'MMM dd, yyyy')}
                  </TableCell>
                  <TableCell sx={{ textAlign: 'center' }}>
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                      <Tooltip title="View Image">
                        <IconButton
                          size="small"
                          onClick={() => handleViewImage(candidate.image)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Download Resume">
                        <IconButton
                          size="small"
                          onClick={() => handleViewResume(candidate.resume)}
                        >
                          <Download />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Assign to Manager">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleAssignClick(candidate)}
                        >
                          <Assignment />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Delete Candidate">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteClick(candidate)}
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {filteredCandidates.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              {candidates.length === 0 
                ? 'No candidates found. Create a new candidate profile to get started.'
                : 'No candidates match the current filters. Try adjusting your search criteria.'
              }
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Assign Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Assign Candidate to Manager</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body1" gutterBottom>
              <strong>Candidate:</strong> {selectedCandidate?.firstName && selectedCandidate?.lastName ? `${selectedCandidate.firstName} ${selectedCandidate.lastName}` : selectedCandidate?.fullName || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Reference:</strong> {selectedCandidate?.referenceNumber}
            </Typography>
            
            <TextField
              fullWidth
              label="Manager Email"
              value={assignForm.managerEmail}
              onChange={(e) => setAssignForm(prev => ({ ...prev, managerEmail: e.target.value }))}
              margin="normal"
              required
              placeholder="Enter manager's email address"
            />
            
            <TextField
              fullWidth
              label="Manager Name (Optional)"
              value={assignForm.managerName}
              onChange={(e) => setAssignForm(prev => ({ ...prev, managerName: e.target.value }))}
              margin="normal"
              placeholder="Enter manager's name for email personalization"
            />

            <TextField
              fullWidth
              label="Schedule Date (Optional)"
              type="datetime-local"
              value={assignForm.scheduleDate}
              onChange={(e) => setAssignForm(prev => ({ ...prev, scheduleDate: e.target.value }))}
              margin="normal"
              InputLabelProps={{
                shrink: true,
              }}
            />

            {/* Email Preview Section */}
            {assignForm.managerEmail && (
              <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  📧 Email Preview
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>To:</strong> {assignForm.managerEmail}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Subject:</strong> New Candidate Assigned – Action Required
                </Typography>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'white', borderRadius: 1, border: '1px solid #ddd' }}>
                  <Typography variant="body2" gutterBottom>
                    Hi {assignForm.managerName || 'Manager'},
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    A new candidate has been assigned to you for interview scheduling and review.
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Candidate Details:</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 2 }} gutterBottom>
                    • Reference #: {selectedCandidate?.referenceNumber}
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 2 }} gutterBottom>
                    • Name: {selectedCandidate?.firstName && selectedCandidate?.lastName ? `${selectedCandidate.firstName} ${selectedCandidate.lastName}` : selectedCandidate?.fullName || 'N/A'}
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 2 }} gutterBottom>
                    • Status: New
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 2 }} gutterBottom>
                    • Scheduled Interview Date: {assignForm.scheduleDate ? new Date(assignForm.scheduleDate).toLocaleString() : 'Not scheduled yet'}
                  </Typography>
                </Box>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleAssignSubmit}
            variant="contained"
            disabled={assignLoading || !assignForm.managerEmail}
          >
            {assignLoading ? <CircularProgress size={20} /> : 'Assign & Send Email'}
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
              This action cannot be undone. All associated data will be permanently deleted.
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

export default CandidatesList; 