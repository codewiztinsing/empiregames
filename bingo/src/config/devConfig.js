// Development configuration for bypassing authentication
export const devConfig = {
  // Check if we're in development mode
  isDevMode: process.env.REACT_APP_DEV_MODE === 'true',
  
  // Check if we should bypass Telegram authentication
  bypassTelegramAuth: process.env.REACT_APP_BYPASS_TELEGRAM_AUTH === 'true',
  
  // Check if we should use mock balance
  useMockBalance: process.env.REACT_APP_USE_MOCK_BALANCE === 'true',
  
  // Mock user data for development
  mockUser: {
    id: 1,
    username: 'dev_user',
    phone: '+251900000000',
    telegram_id: '123456789',
    first_name: 'Dev',
    last_name: 'User',
    is_agent: false,
    referral_code: 'DEV123456789'
  },
  
  // Mock balance data
  mockBalance: {
    balance: 1000.00,
    referral_bonus: 50.00,
    total_balance: 1050.00,
    dev_mode: true,
    mock: true
  },
  
  // Development API endpoints (bypass auth)
  devEndpoints: {
    wallet: '/wallet/dev/player/',
    user: '/users/dev/',
  },
  
  // Check if we should skip authentication for a specific endpoint
  shouldSkipAuth(endpoint) {
    if (!this.isDevMode) return false;
    
    // Skip auth for dev endpoints
    if (endpoint && endpoint.includes('/dev/')) return true;
    
    // Skip auth if bypassing Telegram auth
    if (this.bypassTelegramAuth) return true;
    
    return false;
  },
  
  // Get the appropriate API endpoint
  getEndpoint(baseEndpoint, isDev = false) {
    if (this.isDevMode && (isDev || this.bypassTelegramAuth)) {
      return baseEndpoint.replace('/player/', '/dev/player/');
    }
    return baseEndpoint;
  }
};

export default devConfig;
