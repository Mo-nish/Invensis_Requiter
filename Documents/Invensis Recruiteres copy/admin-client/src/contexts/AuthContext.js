import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Set the base URL for admin API
axios.defaults.baseURL = 'http://localhost:5002';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const adminToken = localStorage.getItem('admin_token');
    if (adminToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${adminToken}`;
      checkAdminAuthStatus();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAdminAuthStatus = async () => {
    try {
      const response = await axios.get('/api/admin/auth/me');
      setAdmin(response.data.admin);
    } catch (error) {
      console.error('Admin auth check failed:', error);
      localStorage.removeItem('admin_token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const adminLogin = async (email, password) => {
    try {
      const response = await axios.post('/api/admin/auth/login', { email, password });
      const { token, admin } = response.data;
      
      localStorage.setItem('admin_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setAdmin(admin);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Admin login failed' 
      };
    }
  };

  const adminRegister = async (adminData) => {
    try {
      const response = await axios.post('/api/admin/auth/register', adminData);
      const { token, admin } = response.data;
      
      localStorage.setItem('admin_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setAdmin(admin);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Admin registration failed' 
      };
    }
  };

  const adminLogout = async () => {
    try {
      await axios.post('/api/admin/auth/logout');
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      localStorage.removeItem('admin_token');
      delete axios.defaults.headers.common['Authorization'];
      setAdmin(null);
    }
  };

  const value = {
    admin,
    loading,
    adminLogin,
    adminRegister,
    adminLogout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 