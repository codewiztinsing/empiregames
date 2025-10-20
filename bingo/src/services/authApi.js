import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AuthApiService {
  constructor() {
    // Normalize base URL and avoid double slashes regardless of REACT_APP_API_URL format
    const baseURL = API_BASE_URL.endsWith('/') ? API_BASE_URL : API_BASE_URL + '/';
    const apiPath = baseURL.includes('/api/v1/') ? 'users' : 'api/v1/users';

    this.api = axios.create({
      baseURL: `${baseURL}${apiPath}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('telegram_auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('telegram_auth_token');
          localStorage.removeItem('telegram_user_data');
          window.location.reload();
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Authenticate with Telegram WebApp data
   */
  async authenticateWithTelegram(telegramData) {
    try {
      const response = await this.api.post('telegram-auth', {
        init_data: telegramData.initData,
        user: telegramData.user,
        auth_date: telegramData.authDate,
        hash: telegramData.hash
      });

      return response.data;
    } catch (error) {
      console.error('Telegram authentication failed:', error);
      throw error;
    }
  }

  /**
   * Register user with Telegram data
   */
  async registerWithTelegram(telegramData, additionalData = {}) {
    try {
      const response = await this.api.post('telegram-register', {
        init_data: telegramData.initData,
        user: telegramData.user,
        auth_date: telegramData.authDate,
        hash: telegramData.hash,
        ...additionalData
      });

      return response.data;
    } catch (error) {
      console.error('Telegram registration failed:', error);
      throw error;
    }
  }

  /**
   * Get user by Telegram ID
   */
  async getUserByTelegramId(telegramId) {
    try {
      const response = await this.api.get(`${telegramId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get user by Telegram ID:', error);
      throw error;
    }
  }

  /**
   * Get user details
   */
  async getUserDetails(userId) {
    try {
      const response = await this.api.get(`${userId}/details/`);
      return response.data;
    } catch (error) {
      console.error('Failed to get user details:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateUserProfile(userId, userData) {
    try {
      const response = await this.api.put(`${userId}/`, userData);
      return response.data;
    } catch (error) {
      console.error('Failed to update user profile:', error);
      throw error;
    }
  }

  /**
   * Check if user has deposited
   */
  async checkDepositStatus(userId) {
    try {
      const response = await this.api.get(`${userId}/is-deposited`);
      return response.data;
    } catch (error) {
      console.error('Failed to check deposit status:', error);
      throw error;
    }
  }

  /**
   * Get user wallet
   */
  async getUserWallet(userId) {
    try {
      const response = await this.api.get(`${userId}/wallet/`);
      return response.data;
    } catch (error) {
      console.error('Failed to get user wallet:', error);
      throw error;
    }
  }

  /**
   * Get user transactions
   */
  async getUserTransactions(userId, limit = 20, transactionType = null) {
    try {
      const params = { limit };
      if (transactionType) {
        params.transaction_type = transactionType;
      }
      
      const response = await this.api.get(`${userId}/transactions/`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get user transactions:', error);
      throw error;
    }
  }

  /**
   * Get user games
   */
  async getUserGames(userId, limit = 20) {
    try {
      const response = await this.api.get(`${userId}/games/`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get user games:', error);
      throw error;
    }
  }

  /**
   * Refresh token
   */
  async refreshToken() {
    try {
      const response = await this.api.get('refresh-token');
      return response.data;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      // Clear local storage
      localStorage.removeItem('telegram_auth_token');
      localStorage.removeItem('telegram_user_data');
      
      // Optionally call logout endpoint if you have one
      // const response = await this.api.post('/logout');
      // return response.data;
      
      return { success: true, message: 'Logged out successfully' };
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }
}

// Create singleton instance
const authApiService = new AuthApiService();

export default authApiService;
