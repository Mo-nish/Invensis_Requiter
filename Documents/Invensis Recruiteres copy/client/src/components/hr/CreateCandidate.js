import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  CircularProgress,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { CloudUpload, Person, Description, Star } from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';

const CreateCandidate = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phoneNumber: '',
    email: '',
    gender: '',
    dateOfBirth: '',
    education: '',
    experience: '',
    technicalTestRating: '',
    hrInterviewRating: '',
    hrReview: ''
  });
  const [files, setFiles] = useState({
    image: null,
    resume: null
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleFileChange = (e) => {
    const { name, files: selectedFiles } = e.target;
    if (selectedFiles && selectedFiles[0]) {
      setFiles(prev => ({
        ...prev,
        [name]: selectedFiles[0]
      }));
      if (errors[name]) {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (formData.phoneNumber.length < 10) {
      newErrors.phoneNumber = 'Phone number must be at least 10 digits';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.gender) {
      newErrors.gender = 'Gender is required';
    }

    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    } else {
      const birthDate = new Date(formData.dateOfBirth);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18 || age > 100) {
        newErrors.dateOfBirth = 'Age must be between 18 and 100 years';
      }
    }

    if (!formData.education.trim()) {
      newErrors.education = 'Education is required';
    }

    if (!formData.experience.trim()) {
      newErrors.experience = 'Experience is required';
    }

    // Validate ratings if provided
    if (formData.technicalTestRating && (formData.technicalTestRating < 1 || formData.technicalTestRating > 10)) {
      newErrors.technicalTestRating = 'Rating must be between 1 and 10';
    }

    if (formData.hrInterviewRating && (formData.hrInterviewRating < 1 || formData.hrInterviewRating > 10)) {
      newErrors.hrInterviewRating = 'Rating must be between 1 and 10';
    }

    if (!files.image) {
      newErrors.image = 'Profile image is required';
    }

    if (!files.resume) {
      newErrors.resume = 'Resume is required';
    } else if (files.resume && files.resume.type !== 'application/pdf') {
      newErrors.resume = 'Resume must be a PDF file';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const formDataToSend = new FormData();
      
      // Append form data
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '') {
          formDataToSend.append(key, formData[key]);
        }
      });
      
      // Append files
      formDataToSend.append('image', files.image);
      formDataToSend.append('resume', files.resume);

      await axios.post('/api/candidates', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Candidate created successfully!');
      
      // Reset form
      setFormData({
        firstName: '',
        lastName: '',
        phoneNumber: '',
        email: '',
        gender: '',
        dateOfBirth: '',
        education: '',
        experience: '',
        technicalTestRating: '',
        hrInterviewRating: '',
        hrReview: ''
      });
      setFiles({
        image: null,
        resume: null
      });
      setErrors({});
      
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to create candidate';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
          Create New Candidate Profile
        </Typography>

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* File Upload Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Upload Files
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ textAlign: 'center', py: 2 }}>
                        <Person sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>
                          Profile Image
                        </Typography>
                        <input
                          accept="image/*"
                          style={{ display: 'none' }}
                          id="image-upload"
                          name="image"
                          type="file"
                          onChange={handleFileChange}
                        />
                        <label htmlFor="image-upload">
                          <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUpload />}
                            sx={{ mb: 1 }}
                          >
                            Upload Image
                          </Button>
                        </label>
                        {files.image && (
                          <Typography variant="body2" color="text.secondary">
                            Selected: {files.image.name}
                          </Typography>
                        )}
                        {errors.image && (
                          <Typography variant="caption" color="error" display="block">
                            {errors.image}
                          </Typography>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ textAlign: 'center', py: 2 }}>
                        <Description sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>
                          Resume (PDF)
                        </Typography>
                        <input
                          accept="application/pdf"
                          style={{ display: 'none' }}
                          id="resume-upload"
                          name="resume"
                          type="file"
                          onChange={handleFileChange}
                        />
                        <label htmlFor="resume-upload">
                          <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUpload />}
                            sx={{ mb: 1 }}
                          >
                            Upload Resume
                          </Button>
                        </label>
                        {files.resume && (
                          <Typography variant="body2" color="text.secondary">
                            Selected: {files.resume.name}
                          </Typography>
                        )}
                        {errors.resume && (
                          <Typography variant="caption" color="error" display="block">
                            {errors.resume}
                          </Typography>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>

            {/* Personal Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Personal Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="First Name"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                error={!!errors.firstName}
                helperText={errors.firstName}
                placeholder="Enter First Name"
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Last Name"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                error={!!errors.lastName}
                helperText={errors.lastName}
                placeholder="Enter Last Name"
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone Number"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                error={!!errors.phoneNumber}
                helperText={errors.phoneNumber}
                placeholder="Enter Phone Number"
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!errors.email}
                helperText={errors.email}
                placeholder="Enter Email Address"
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.gender}>
                <InputLabel>Gender</InputLabel>
                <Select
                  name="gender"
                  value={formData.gender}
                  label="Gender"
                  onChange={handleChange}
                >
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
                {errors.gender && (
                  <Typography variant="caption" color="error" display="block">
                    {errors.gender}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Date of Birth"
                name="dateOfBirth"
                type="date"
                value={formData.dateOfBirth}
                onChange={handleChange}
                error={!!errors.dateOfBirth}
                helperText={errors.dateOfBirth}
                required
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            {/* Education and Experience */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Education & Experience
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Education"
                name="education"
                multiline
                rows={3}
                value={formData.education}
                onChange={handleChange}
                error={!!errors.education}
                helperText={errors.education}
                placeholder="Enter educational background..."
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Work Experience"
                name="experience"
                multiline
                rows={4}
                value={formData.experience}
                onChange={handleChange}
                error={!!errors.experience}
                helperText={errors.experience}
                placeholder="Enter work experience details..."
                required
              />
            </Grid>

            {/* Ratings Section */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Star color="primary" />
                Ratings
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Technical Test Rating"
                name="technicalTestRating"
                type="number"
                value={formData.technicalTestRating}
                onChange={handleChange}
                error={!!errors.technicalTestRating}
                helperText={errors.technicalTestRating || "Rate from 1-10 (optional)"}
                placeholder="Enter rating 1-10"
                inputProps={{
                  min: 1,
                  max: 10
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="HR Interview Rating"
                name="hrInterviewRating"
                type="number"
                value={formData.hrInterviewRating}
                onChange={handleChange}
                error={!!errors.hrInterviewRating}
                helperText={errors.hrInterviewRating || "Rate from 1-10 (optional)"}
                placeholder="Enter rating 1-10"
                inputProps={{
                  min: 1,
                  max: 10
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="HR Review (Note)"
                name="hrReview"
                multiline
                rows={4}
                value={formData.hrReview}
                onChange={handleChange}
                error={!!errors.hrReview}
                helperText={errors.hrReview}
                placeholder="Enter HR review notes and comments..."
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ px: 4, py: 1.5 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Submit'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateCandidate; 