import React, { useState, useMemo, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  OutlinedInput,
  Checkbox,
  ListItemText,
  CircularProgress
} from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const COLORS = {
  'New': '#2196F3',
  'Assigned': '#FF9800',
  'Under Review': '#9C27B0',
  'Interview Scheduled': '#607D8B',
  'Shortlisted': '#4CAF50',
  'Rejected': '#F44336',
  'On Hold': '#FFC107',
  'Reassigned to HR': '#795548'
};

const DashboardHome = ({ 
  data, 
  title, 
  showRoleFilter = false,
  userRole = null,
  loading = false
}) => {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [statusFilter, setStatusFilter] = useState([]);
  const [roleFilter, setRoleFilter] = useState('all');

  // Debug logging
  useEffect(() => {
    console.log('DashboardHome data:', data);
    console.log('DashboardHome data type:', typeof data);
    console.log('DashboardHome isArray:', Array.isArray(data));
  }, [data]);

  // Filter data based on selected filters
  const filteredData = useMemo(() => {
    // Ensure data is an array
    if (!Array.isArray(data)) {
      console.warn('DashboardHome: data is not an array', data);
      return [];
    }

    let filtered = data;

    // Date filter
    if (dateFrom || dateTo) {
      filtered = filtered.filter(item => {
        const itemDate = new Date(item.createdAt || item.assignedAt);
        if (dateFrom) {
          const fromDate = new Date(dateFrom);
          if (itemDate < fromDate) return false;
        }
        if (dateTo) {
          const toDate = new Date(dateTo);
          toDate.setHours(23, 59, 59, 999);
          if (itemDate > toDate) return false;
        }
        return true;
      });
    }

    // Status filter
    if (statusFilter.length > 0) {
      filtered = filtered.filter(item => 
        statusFilter.includes(item.status)
      );
    }

    // Role filter (if applicable)
    if (showRoleFilter && roleFilter !== 'all') {
      filtered = filtered.filter(item => 
        item.assignedTo?.designation === roleFilter
      );
    }

    return filtered;
  }, [data, dateFrom, dateTo, statusFilter, roleFilter, showRoleFilter]);

  // Calculate status counts
  const statusCounts = useMemo(() => {
    const counts = {};
    const statuses = ['New', 'Assigned', 'Under Review', 'Interview Scheduled', 'Shortlisted', 'Rejected', 'On Hold', 'Reassigned to HR'];
    
    statuses.forEach(status => {
      counts[status] = 0;
    });

    // Ensure filteredData is an array before using forEach
    if (!Array.isArray(filteredData)) {
      console.warn('DashboardHome: filteredData is not an array', filteredData);
      return counts;
    }

    filteredData.forEach(item => {
      const status = item.status;
      if (counts.hasOwnProperty(status)) {
        counts[status]++;
      }
    });

    return counts;
  }, [filteredData]);

  // Prepare chart data
  const chartData = useMemo(() => {
    return Object.entries(statusCounts)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => ({
        name: status,
        value: count,
        color: COLORS[status] || '#999'
      }));
  }, [statusCounts]);

  const totalCount = Object.values(statusCounts).reduce((sum, count) => sum + count, 0);

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '50vh', gap: 2 }}>
          <CircularProgress size={60} />
          <Typography variant="h6" color="text.secondary">
            Loading dashboard data...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          {title}
        </Typography>
        
        {/* Filters */}
        <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="date"
                label="From Date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="date"
                label="To Date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status Filter</InputLabel>
                <Select
                  multiple
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  input={<OutlinedInput label="Status Filter" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  sx={{ borderRadius: 2 }}
                >
                  {Object.keys(COLORS).map((status) => (
                    <MenuItem key={status} value={status}>
                      <Checkbox checked={statusFilter.indexOf(status) > -1} />
                      <ListItemText primary={status} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            {showRoleFilter && (
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Role Filter</InputLabel>
                  <Select
                    value={roleFilter}
                    label="Role Filter"
                    onChange={(e) => setRoleFilter(e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="all">All Roles</MenuItem>
                    <MenuItem value="HR">HR</MenuItem>
                    <MenuItem value="Manager">Manager</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
          </Grid>
        </Paper>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <CardContent sx={{ textAlign: 'center', color: 'white' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                  {totalCount}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Total Candidates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <CardContent sx={{ textAlign: 'center', color: 'white' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                  {statusCounts['Shortlisted'] || 0}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Shortlisted
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <CardContent sx={{ textAlign: 'center', color: 'white' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                  {statusCounts['Under Review'] || 0}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  In Progress
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <CardContent sx={{ textAlign: 'center', color: 'white' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                  {statusCounts['New'] || 0}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  New Candidates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Additional Analytics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', color: '#ff6b35' }}>
                  {statusCounts['Rejected'] || 0}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Rejected
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                  {statusCounts['On Hold'] || 0}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  On Hold
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={3} sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', color: '#ff6b9d' }}>
                  {statusCounts['Interview Scheduled'] || 0}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Interview Scheduled
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                Status Overview
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>

        {/* Status Breakdown Cards */}
        <Grid container spacing={2} sx={{ mt: 3 }}>
          {Object.entries(statusCounts).map(([status, count]) => (
            <Grid item xs={12} sm={6} md={3} key={status}>
              <Card elevation={2} sx={{ borderRadius: 2, borderLeft: `4px solid ${COLORS[status] || '#999'}` }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: COLORS[status] }}>
                      {count}
                    </Typography>
                    <Box sx={{ 
                      width: 40, 
                      height: 40, 
                      borderRadius: '50%', 
                      backgroundColor: COLORS[status],
                      opacity: 0.2 
                    }} />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {status}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default DashboardHome; 