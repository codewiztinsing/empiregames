import axios from 'axios';
import config from '../config/api';

// Normalize base URL to ensure trailing slash
const baseURL = config.API_BASE_URL.endsWith('/') ? config.API_BASE_URL : `${config.API_BASE_URL}/`;

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach bearer token from localStorage
apiClient.interceptors.request.use((cfg) => {
  try {
    // Check if we're in development mode and bypassing auth
    const isDevMode = process.env.REACT_APP_DEV_MODE === 'true';
    const bypassAuth = process.env.REACT_APP_BYPASS_TELEGRAM_AUTH === 'true';
    const isDevEndpoint = cfg.url && cfg.url.includes('/dev/');
    
    // Skip auth for dev endpoints or when bypassing auth in dev mode
    if (isDevMode && (bypassAuth || isDevEndpoint)) {
      console.log('[APIClientDebug] Skipping auth for dev request:', cfg.url);
      return cfg;
    }
    
    const token = localStorage.getItem('telegram_auth_token');
    if (token) {
      cfg.headers.Authorization = `Bearer ${token}`;
    }
    // Debug request auth presence
    try {
      const auth = cfg.headers.Authorization;
      const path = (cfg.url || '').toString();
      if (path.includes('wallet/player')) {
        console.log('[APIClientDebug] Request', { url: cfg.baseURL + path, hasAuth: !!auth, authPrefix: auth ? auth.slice(0, 24) : null });
      }
    } catch (_) {}
  } catch (e) {}
  return cfg;
});

// Convenience APIs
export const walletApi = {
  // Backend expects telegram_id for this endpoint
  getPlayerWalletByTelegram(telegramId) {
    // Use development endpoint if in dev mode and bypassing auth
    const isDevMode = process.env.REACT_APP_DEV_MODE === 'true';
    const bypassAuth = process.env.REACT_APP_BYPASS_TELEGRAM_AUTH === 'true';
    
    if (isDevMode && bypassAuth) {
      const url = `wallet/dev/player/${parseInt(telegramId)}`;
      console.log('[WalletApi] Using dev endpoint (no auth required):', url);
      return apiClient.get(url);
    } else {
      const url = `wallet/player/${parseInt(telegramId)}`;
      console.log('[WalletApi] Using production endpoint (auth required):', url);
      return apiClient.get(url);
    }
  },
};

export default apiClient;


