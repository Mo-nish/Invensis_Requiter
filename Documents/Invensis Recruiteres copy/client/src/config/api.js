// API Configuration for different environments
const getApiConfig = () => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  if (isDevelopment) {
    return {
      baseURL: 'http://localhost:5001',
      adminURL: 'http://localhost:5002'
    };
  }
  
  // Production URLs - these will be your Render deployment URLs
  return {
    baseURL: process.env.REACT_APP_API_URL || 'https://invensis-hiring-server.onrender.com',
    adminURL: process.env.REACT_APP_ADMIN_API_URL || 'https://invensis-admin-server.onrender.com'
  };
};

export const apiConfig = getApiConfig();

export default apiConfig; 