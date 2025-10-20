// API Configuration (normalized)
const rawBase = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1/';

const ensureTrailingSlash = (url) => (url?.endsWith('/') ? url : `${url}/`);

const addApiPrefixIfMissing = (url) => {
  const withSlash = ensureTrailingSlash(url);
  // If already contains /api/v1/, keep it, else append it
  if (withSlash.includes('/api/v1/')) return withSlash;
  return ensureTrailingSlash(`${withSlash}api/v1`);
};

const API_BASE_URL = addApiPrefixIfMissing(rawBase);

const config = {
  API_BASE_URL,
  SOCKET_URL: process.env.REACT_APP_SOCKET_URL || 'http://localhost:3001',
  ENV: process.env.REACT_APP_ENV || 'development'
};

export default config;
