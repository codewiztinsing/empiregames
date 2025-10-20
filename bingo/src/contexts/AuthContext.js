import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import telegramAuthService from '../services/telegramAuth';
import authApiService from '../services/authApi';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Development mode bypass
  const isDevMode = process.env.REACT_APP_DEV_MODE === 'true';
  const bypassTelegramAuth = process.env.REACT_APP_BYPASS_TELEGRAM_AUTH === 'true';

  // Initialize Telegram WebApp
  useEffect(() => {
    const initializeTelegram = () => {
      try {
        if (bypassTelegramAuth) {
          console.log('Development mode: Bypassing Telegram WebApp initialization');
          return;
        }
        telegramAuthService.init();
        console.log('Telegram WebApp initialized');
      } catch (error) {
        console.error('Failed to initialize Telegram WebApp:', error);
        if (!bypassTelegramAuth) {
          setError('Failed to initialize Telegram WebApp');
        }
      }
    };

    initializeTelegram();
  }, [bypassTelegramAuth]);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkExistingAuth = async () => {
      try {
        if (bypassTelegramAuth) {
          // Development mode: Use mock user data
          const mockUser = {
            id: 1,
            username: 'dev_user',
            phone: '+251900000000',
            telegram_id: '123456789',
            first_name: 'Dev',
            last_name: 'User',
            is_agent: false,
            referral_code: 'DEV123456789'
          };
          const mockToken = 'dev_token_' + Date.now();
          
          setToken(mockToken);
          setUser(mockUser);
          setIsAuthenticated(true);
          localStorage.setItem('telegram_user_data', JSON.stringify(mockUser));
          localStorage.setItem('dev_token', mockToken);
          console.log('Development mode: Using mock authentication');
        } else {
          const storedToken = telegramAuthService.getToken();
          const storedUser = localStorage.getItem('telegram_user_data');
          
          if (storedToken && storedUser) {
            const userData = JSON.parse(storedUser);
            setToken(storedToken);
            setUser(userData);
            setIsAuthenticated(true);
          }
        }
      } catch (error) {
        console.error('Error checking existing auth:', error);
        if (!bypassTelegramAuth) {
          telegramAuthService.clearAuth();
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingAuth();
  }, [bypassTelegramAuth]);

  // Login function
  const login = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      if (bypassTelegramAuth) {
        // Development mode: Return mock success
        const mockUser = {
          id: 1,
          username: 'dev_user',
          phone: '+251900000000',
          telegram_id: '123456789',
          first_name: 'Dev',
          last_name: 'User',
          is_agent: false,
          referral_code: 'DEV123456789'
        };
        const mockToken = 'dev_token_' + Date.now();
        
        setToken(mockToken);
        setUser(mockUser);
        setIsAuthenticated(true);

        // Ensure axios client can send auth header
        telegramAuthService.setToken(mockToken);
        localStorage.setItem('telegram_user_data', JSON.stringify(mockUser));
        localStorage.setItem('dev_token', mockToken);
        
        return { success: true, isNewUser: false };
      }

      // Get Telegram user data
      const telegramData = telegramAuthService.getTelegramUser();
      if (!telegramData) {
        throw new Error('Failed to get Telegram user data');
      }

      // Try to authenticate with existing user
      try {
        const authResponse = await authApiService.authenticateWithTelegram(telegramData);
        
        if (authResponse.success) {
          setToken(authResponse.token);
          setUser(authResponse.user);
          setIsAuthenticated(true);
          // Persist token for apiClient
          telegramAuthService.setToken(authResponse.token);
          localStorage.setItem('telegram_user_data', JSON.stringify(authResponse.user));
          console.log('[AuthDebug] Telegram auth success; token set to localStorage');
          
          return { success: true, isNewUser: false };
        }
      } catch (authError) {
        // If authentication fails, user might not exist
        if (authError.response?.status === 404) {
          return { success: false, isNewUser: true, telegramData };
        }
        throw authError;
      }
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message || 'Login failed');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, [bypassTelegramAuth]);

  // Register function
  const register = useCallback(async (telegramData, additionalData = {}) => {
    try {
      setIsLoading(true);
      setError(null);

      const registerResponse = await authApiService.registerWithTelegram(telegramData, additionalData);
      
      if (registerResponse.success) {
        setToken(registerResponse.token);
        setUser(registerResponse.user);
        setIsAuthenticated(true);
        // Persist token for apiClient
        telegramAuthService.setToken(registerResponse.token);
        localStorage.setItem('telegram_user_data', JSON.stringify(registerResponse.user));
        console.log('[AuthDebug] Telegram register success; token set to localStorage');
        
        return { success: true, user: registerResponse.user };
      } else {
        throw new Error(registerResponse.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.message || 'Registration failed');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Call logout API
      await authApiService.logout();
      
      // Clear local state
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
      setError(null);
      
      // Clear stored data
      telegramAuthService.clearAuth();
      
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      // Even if API call fails, clear local state
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
      telegramAuthService.clearAuth();
      
      return { success: true };
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Refresh user data
  const refreshUser = useCallback(async () => {
    if (!user?.id) return;

    try {
      const userDetails = await authApiService.getUserDetails(user.id);
      setUser(prevUser => ({ ...prevUser, ...userDetails.user }));
      localStorage.setItem('telegram_user_data', JSON.stringify({ ...user, ...userDetails.user }));
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  }, [user?.id]);

  // Check if user has deposited
  const checkDepositStatus = useCallback(async () => {
    if (!user?.telegram_id) return false;

    try {
      const depositStatus = await authApiService.checkDepositStatus(user.telegram_id);
      return depositStatus.is_deposited || false;
    } catch (error) {
      console.error('Failed to check deposit status:', error);
      return false;
    }
  }, [user?.telegram_id]);

  // Get user wallet
  const getUserWallet = useCallback(async () => {
    if (!user?.id) return null;

    try {
      const walletData = await authApiService.getUserWallet(user.id);
      return walletData;
    } catch (error) {
      console.error('Failed to get user wallet:', error);
      return null;
    }
  }, [user?.id]);

  // Get user transactions
  const getUserTransactions = useCallback(async (limit = 20, transactionType = null) => {
    if (!user?.id) return null;

    try {
      const transactions = await authApiService.getUserTransactions(user.id, limit, transactionType);
      return transactions;
    } catch (error) {
      console.error('Failed to get user transactions:', error);
      return null;
    }
  }, [user?.id]);

  // Get user games
  const getUserGames = useCallback(async (limit = 20) => {
    if (!user?.id) return null;

    try {
      const games = await authApiService.getUserGames(user.id, limit);
      return games;
    } catch (error) {
      console.error('Failed to get user games:', error);
      return null;
    }
  }, [user?.id]);

  // Update user profile
  const updateProfile = useCallback(async (userData) => {
    if (!user?.id) return { success: false, error: 'No user logged in' };

    try {
      const response = await authApiService.updateUserProfile(user.id, userData);
      
      // Update local user state
      setUser(prevUser => ({ ...prevUser, ...userData }));
      localStorage.setItem('telegram_user_data', JSON.stringify({ ...user, ...userData }));
      
      return { success: true, user: { ...user, ...userData } };
    } catch (error) {
      console.error('Failed to update profile:', error);
      return { success: false, error: error.message };
    }
  }, [user]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Telegram WebApp utilities
  const showAlert = useCallback((message) => {
    telegramAuthService.showAlert(message);
  }, []);

  const showConfirm = useCallback((message, callback) => {
    telegramAuthService.showConfirm(message, callback);
  }, []);

  const closeApp = useCallback(() => {
    telegramAuthService.close();
  }, []);

  const sendDataToBot = useCallback((data) => {
    telegramAuthService.sendData(data);
  }, []);

  const getMainButton = useCallback(() => {
    return telegramAuthService.getMainButton();
  }, []);

  const getBackButton = useCallback(() => {
    return telegramAuthService.getBackButton();
  }, []);

  const getHapticFeedback = useCallback(() => {
    return telegramAuthService.getHapticFeedback();
  }, []);

  const value = {
    // Auth state
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    
    // Auth actions
    login,
    register,
    logout,
    refreshUser,
    clearError,
    
    // User data actions
    checkDepositStatus,
    getUserWallet,
    getUserTransactions,
    getUserGames,
    updateProfile,
    
    // Telegram WebApp utilities
    showAlert,
    showConfirm,
    closeApp,
    sendDataToBot,
    getMainButton,
    getBackButton,
    getHapticFeedback,
    
    // Telegram WebApp info
    isTelegram: telegramAuthService.isTelegram(),
    platform: telegramAuthService.getPlatform(),
    version: telegramAuthService.getVersion(),
    theme: telegramAuthService.getTheme(),
    colorScheme: telegramAuthService.getColorScheme(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
