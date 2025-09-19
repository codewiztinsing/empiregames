import config from '../config/api';

const API_BASE_URL = config.API_BASE_URL;

class ReferralApiService {
  constructor() {
    // Ensure no double slashes by removing trailing slash from API_BASE_URL
    const cleanApiUrl = API_BASE_URL.replace(/\/$/, '');
    this.baseURL = `${cleanApiUrl}/referrals`;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    console.log('Referral API URL:', url);
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    };

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // User endpoints
  async setReferrer(referralCode) {
    return this.makeRequest('/set-referrer', {
      method: 'POST',
      body: JSON.stringify({ referral_code: referralCode }),
    });
  }

  async getStats() {
    return this.makeRequest('/stats');
  }

  async getBonuses() {
    return this.makeRequest('/bonuses');
  }

  async createWithdrawalRequest(amount) {
    return this.makeRequest('/withdrawal-request', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
  }

  async getWithdrawals() {
    return this.makeRequest('/withdrawals');
  }

  async getAnnouncements() {
    return this.makeRequest('/announcements');
  }

  // Admin endpoints
  async getAllBonuses() {
    return this.makeRequest('/admin/bonuses');
  }

  async approveBonus(bonusId) {
    return this.makeRequest(`/admin/bonuses/${bonusId}/approve`, {
      method: 'POST',
    });
  }

  async getAllWithdrawals() {
    return this.makeRequest('/admin/withdrawals');
  }

  async approveWithdrawal(withdrawalId) {
    return this.makeRequest(`/admin/withdrawals/${withdrawalId}/approve`, {
      method: 'POST',
    });
  }

  async rejectWithdrawal(withdrawalId) {
    return this.makeRequest(`/admin/withdrawals/${withdrawalId}/reject`, {
      method: 'POST',
    });
  }
}

export default new ReferralApiService();
