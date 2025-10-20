import { useAuth } from '../contexts/AuthContext';
import { useCallback } from 'react';

export const useTelegramAuth = () => {
  const auth = useAuth();

  const handleLogin = useCallback(async () => {
    const result = await auth.login();
    
    if (result.success) {
      auth.showAlert('Welcome back! You are now logged in.');
      return result;
    } else if (result.isNewUser) {
      // User needs to register
      return result;
    } else {
      auth.showAlert(result.error || 'Login failed. Please try again.');
      return result;
    }
  }, [auth]);

  const handleRegister = useCallback(async (telegramData, additionalData = {}) => {
    const result = await auth.register(telegramData, additionalData);
    
    if (result.success) {
      auth.showAlert('Registration successful! Welcome to the game!');
      return result;
    } else {
      auth.showAlert(result.error || 'Registration failed. Please try again.');
      return result;
    }
  }, [auth]);

  const handleLogout = useCallback(async () => {
    const result = await auth.logout();
    
    if (result.success) {
      auth.showAlert('You have been logged out successfully.');
      return result;
    } else {
      auth.showAlert('Logout failed. Please try again.');
      return result;
    }
  }, [auth]);

  const handleCompleteAuth = useCallback(async () => {
    // Try to login first
    const loginResult = await handleLogin();
    
    if (loginResult.success) {
      return loginResult;
    } else if (loginResult.isNewUser) {
      // User needs to register
      const telegramData = loginResult.telegramData;
      
      // Show registration confirmation
      return new Promise((resolve) => {
        auth.showConfirm(
          'Welcome! You need to register to continue. Would you like to register now?',
          async (confirmed) => {
            if (confirmed) {
              const registerResult = await handleRegister(telegramData);
              resolve(registerResult);
            } else {
              resolve({ success: false, error: 'Registration cancelled' });
            }
          }
        );
      });
    } else {
      return loginResult;
    }
  }, [auth, handleLogin, handleRegister]);

  return {
    ...auth,
    handleLogin,
    handleRegister,
    handleLogout,
    handleCompleteAuth,
  };
};

export default useTelegramAuth;
