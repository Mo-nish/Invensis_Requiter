import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Delete,
  Email,
  Person,
  Schedule,
  CheckCircle,
  Cancel
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';

const RoleManagement = ({ role }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ email: '' });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAssignments();
  }, [role]);

  const fetchAssignments = async () => {
    try {
      const response = await axios.get('/api/admin/roles');
      const roleAssignments = response.data.assignments[role] || [];
      setAssignments(roleAssignments);
    } catch (error) {
      console.error('Fetch assignments error:', error);
      toast.error('Failed to fetch role assignments');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAssignment = async () => {
    if (!formData.email.trim()) {
      setFormErrors({ email: 'Email is required' });
      return;
    }

    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setFormErrors({ email: 'Please enter a valid email' });
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post('/api/admin/roles', {
        email: formData.email,
        role
      });

      toast.success('Role assignment created successfully!');
      setAddDialogOpen(false);
      setFormData({ email: '' });
      setFormErrors({});
      fetchAssignments();
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to create role assignment';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteAssignment = async (assignmentId) => {
    if (!window.confirm('Are you sure you want to delete this role assignment?')) {
      return;
    }

    try {
      await axios.delete(`/api/admin/roles/${assignmentId}`);
      toast.success('Role assignment deleted successfully!');
      fetchAssignments();
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to delete role assignment';
      toast.error(message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'pending':
        return 'warning';
      case 'inactive':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle />;
      case 'pending':
        return <Schedule />;
      case 'inactive':
        return <Cancel />;
      default:
        return null;
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
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          {role} Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddDialogOpen(true)}
        >
          Add {role}
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total {role}s
              </Typography>
              <Typography variant="h4">
                {assignments.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active
              </Typography>
              <Typography variant="h4" color="success.main">
                {assignments.filter(a => a.isActive).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending
              </Typography>
              <Typography variant="h4" color="warning.main">
                {assignments.filter(a => a.status === 'pending').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Registered
              </Typography>
              <Typography variant="h4" color="primary.main">
                {assignments.filter(a => a.registeredAt).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assignments Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Invited By</TableCell>
                <TableCell>Invited Date</TableCell>
                <TableCell>Registered Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assignments.map((assignment) => (
                <TableRow key={assignment._id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Email sx={{ mr: 1, color: 'text.secondary' }} />
                      {assignment.email}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={getStatusIcon(assignment.status)}
                      label={assignment.status}
                      color={getStatusColor(assignment.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {assignment.invitedBy?.name || 'N/A'}
                  </TableCell>
                  <TableCell>
                    {new Date(assignment.invitedAt).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {assignment.registeredAt 
                      ? new Date(assignment.registeredAt).toLocaleDateString()
                      : 'Not registered'
                    }
                  </TableCell>
                  <TableCell>
                    <IconButton
                      color="error"
                      size="small"
                      onClick={() => handleDeleteAssignment(assignment._id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Add Assignment Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add {role}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email Address"
            name="email"
            type="email"
            value={formData.email}
            onChange={(e) => {
              setFormData({ email: e.target.value });
              if (formErrors.email) {
                setFormErrors({});
              }
            }}
            error={!!formErrors.email}
            helperText={formErrors.email}
            margin="normal"
            placeholder={`Enter ${role.toLowerCase()} email address`}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            An email notification will be sent to the user with registration instructions.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleAddAssignment}
            variant="contained"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={20} /> : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RoleManagement; 