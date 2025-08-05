import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import { Delete as DeleteIcon, Email as EmailIcon } from '@mui/icons-material';
import { toast } from 'react-toastify';

const RoleManagement = () => {
  const [assignments, setAssignments] = useState([]);
  const [limits, setLimits] = useState({});
  const [currentCounts, setCurrentCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [addingUser, setAddingUser] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    role: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchAssignments();
    fetchLimits();
  }, []);

  const fetchAssignments = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/admin/roles', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAssignments(data);
      } else {
        toast.error('Failed to fetch role assignments');
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
      toast.error('Failed to fetch role assignments');
    }
  };

  const fetchLimits = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/admin/roles/limits', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setLimits(data.limits);
        setCurrentCounts(data.currentCounts);
      } else {
        toast.error('Failed to fetch role limits');
      }
    } catch (error) {
      console.error('Error fetching limits:', error);
      toast.error('Failed to fetch role limits');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    
    // Validate form
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.role) newErrors.role = 'Role is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setAddingUser(true);
    setErrors({});

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/admin/roles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        toast.success('User added successfully');
        setFormData({ email: '', role: '' });
        fetchAssignments();
        fetchLimits();
      } else {
        toast.error(result.message || 'Failed to add user');
      }
    } catch (error) {
      console.error('Error adding user:', error);
      toast.error('Failed to add user');
    } finally {
      setAddingUser(false);
    }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/admin/roles/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        toast.success('User deleted successfully');
        fetchAssignments();
        fetchLimits();
      } else {
        toast.error('Failed to delete user');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Failed to delete user');
    }
  };

  const getRoleColor = (role) => {
    const count = currentCounts[role] || 0;
    const limit = limits[role] || 0;
    const percentage = (count / limit) * 100;
    
    if (percentage >= 90) return 'error';
    if (percentage >= 75) return 'warning';
    return 'success';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Role Management
      </Typography>

      {/* Role Limits Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {Object.keys(limits).map((role) => {
          const count = currentCounts[role] || 0;
          const limit = limits[role];
          const percentage = (count / limit) * 100;
          
          return (
            <Grid item xs={12} sm={6} md={3} key={role}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {role}
                  </Typography>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h4" color={getRoleColor(role)}>
                      {count}/{limit}
                    </Typography>
                    <Chip 
                      label={`${percentage.toFixed(0)}%`}
                      color={getRoleColor(role)}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {count >= limit ? 'Limit reached' : `${limit - count} slots available`}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Add User Form */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Add New User
          </Typography>
          <Box component="form" onSubmit={handleAddUser}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email Address"
                  name="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  error={!!errors.email}
                  helperText={errors.email}
                  disabled={addingUser}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth error={!!errors.role}>
                  <InputLabel>Role</InputLabel>
                  <Select
                    name="role"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    disabled={addingUser}
                  >
                    <MenuItem value="HR">HR</MenuItem>
                    <MenuItem value="Manager">Manager</MenuItem>
                    <MenuItem value="Board Member">Board Member</MenuItem>
                  </Select>
                  {errors.role && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                      {errors.role}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={addingUser || !formData.email || !formData.role}
                  sx={{ height: '56px' }}
                >
                  {addingUser ? <CircularProgress size={24} /> : 'Add User'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>

      {/* Role Limits Alert */}
      {Object.keys(limits).some(role => {
        const count = currentCounts[role] || 0;
        const limit = limits[role];
        return count >= limit;
      }) && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Some roles have reached their limits. Users cannot be added to these roles until existing users are removed.
        </Alert>
      )}

      {/* Users Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Users
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Invited By</TableCell>
                  <TableCell>Invited At</TableCell>
                  <TableCell>Registered At</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assignments.map((assignment) => (
                  <TableRow key={assignment._id}>
                    <TableCell>{assignment.email}</TableCell>
                    <TableCell>
                      <Chip 
                        label={assignment.role}
                        color={getRoleColor(assignment.role)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={assignment.status}
                        color={getStatusColor(assignment.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {assignment.invitedBy?.name || 'Unknown'}
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
                        onClick={() => handleDeleteUser(assignment._id)}
                        color="error"
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Container>
  );
};

export default RoleManagement; 