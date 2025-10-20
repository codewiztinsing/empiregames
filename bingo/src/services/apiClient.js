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
    const url = `wallet/player/${parseInt(telegramId)}`;
    return apiClient.get(url);
  },
};

export default apiClient;


