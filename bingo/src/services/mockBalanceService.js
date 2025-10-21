import { walletApi } from './apiClient';

// Mock balance service for development
export const mockBalanceService = {
  getPlayerWalletByTelegram(telegramId) {
    console.log('[MockBalance] Returning mock balance for telegram_id:', telegramId);
    
    // Return a mock response that matches the real API structure
    return Promise.resolve({
      data: {
        balance: 1000.00,
        referral_bonus: 50.00,
        total_balance: 1050.00,
        dev_mode: true,
        mock: true
      }
    });
  }
};

// Development balance service that switches between real and mock
export const devBalanceService = {
  getPlayerWalletByTelegram(telegramId) {
    const useMock = process.env.REACT_APP_USE_MOCK_BALANCE === 'true';
    
    if (useMock) {
      return mockBalanceService.getPlayerWalletByTelegram(telegramId);
    } else {
      // Use the real API client
      return walletApi.getPlayerWalletByTelegram(telegramId);
    }
  }
};
