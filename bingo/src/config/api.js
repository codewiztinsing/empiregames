// API Configuration
const config = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  SOCKET_URL: process.env.REACT_APP_SOCKET_URL || 'http://localhost:3001',
  ENV: process.env.REACT_APP_ENV || 'development'
};

export default config;
