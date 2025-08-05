import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Paper
} from '@mui/material';
import { Search } from '@mui/icons-material';

const FilterBar = ({ 
  searchValue, 
  onSearchChange, 
  statusFilter, 
  onStatusFilterChange,
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange
}) => {
  return (
    <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', md: 'row' }, 
        gap: 2, 
        alignItems: { xs: 'stretch', md: 'center' } 
      }}>
        {/* Search Bar */}
        <Box sx={{ flex: 1, minWidth: { xs: '100%', md: '300px' } }}>
          <TextField
            fullWidth
            placeholder="Search by Reference #, Name, or Email..."
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                backgroundColor: 'background.paper',
              }
            }}
          />
        </Box>

        {/* Status Filter */}
        <FormControl sx={{ minWidth: { xs: '100%', md: '150px' } }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            label="Status"
            onChange={(e) => onStatusFilterChange(e.target.value)}
            sx={{
              borderRadius: 2,
              backgroundColor: 'background.paper',
            }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="New">New</MenuItem>
            <MenuItem value="Assigned">Assigned</MenuItem>
            <MenuItem value="Under Review">In Progress</MenuItem>
            <MenuItem value="Interview Scheduled">Interview Scheduled</MenuItem>
            <MenuItem value="Shortlisted">Shortlisted</MenuItem>
            <MenuItem value="Rejected">Rejected</MenuItem>
            <MenuItem value="On Hold">On Hold</MenuItem>
            <MenuItem value="Reassigned to HR">Reassigned to HR</MenuItem>
          </Select>
        </FormControl>

        {/* Date Range Filters */}
        <TextField
          type="date"
          label="From Date"
          value={dateFrom}
          onChange={(e) => onDateFromChange(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{
            minWidth: { xs: '100%', md: '150px' },
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: 'background.paper',
            }
          }}
        />

        <TextField
          type="date"
          label="To Date"
          value={dateTo}
          onChange={(e) => onDateToChange(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{
            minWidth: { xs: '100%', md: '150px' },
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: 'background.paper',
            }
          }}
        />
      </Box>
    </Paper>
  );
};

export default FilterBar; 