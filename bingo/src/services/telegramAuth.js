import WebApp from '@twa-dev/sdk';

class TelegramAuthService {
  constructor() {
    this.webApp = WebApp;
    this.isInitialized = false;
    this.user = null;
    this.token = null;
  }

  /**
   * Initialize Telegram WebApp
   */
  init() {
    if (this.isInitialized) return;
    
    try {
      this.webApp.ready();
      this.webApp.expand();
      
      // Enable closing confirmation
      this.webApp.enableClosingConfirmation();
      
      this.isInitialized = true;
      console.log('Telegram WebApp initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Telegram WebApp:', error);
    }
  }

  /**
   * Get Telegram user data
   */
  getTelegramUser() {
    if (!this.isInitialized) {
      this.init();
    }
    
    try {
      const initData = this.webApp.initData;
      const user = this.webApp.initDataUnsafe?.user;
      
      if (user) {
        this.user = {
          id: user.id,
          first_name: user.first_name,
          last_name: user.last_name,
          username: user.username,
          language_code: user.language_code,
          is_premium: user.is_premium || false,
          photo_url: user.photo_url
        };
        
        return {
          user: this.user,
          initData: initData,
          authDate: this.webApp.initDataUnsafe?.auth_date,
          hash: this.webApp.initDataUnsafe?.hash
        };
      }
      
      return null;
    } catch (error) {
      console.error('Failed to get Telegram user:', error);
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return this.token !== null && this.user !== null;
  }

  /**
   * Get stored token
   */
  getToken() {
    return this.token || localStorage.getItem('telegram_auth_token');
  }

  /**
   * Set authentication token
   */
  setToken(token) {
    this.token = token;
    localStorage.setItem('telegram_auth_token', token);
  }

  /**
   * Clear authentication data
   */
  clearAuth() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('telegram_auth_token');
    localStorage.removeItem('telegram_user_data');
  }

  /**
   * Get Telegram WebApp theme
   */
  getTheme() {
    return this.webApp.themeParams;
  }

  /**
   * Get Telegram WebApp color scheme
   */
  getColorScheme() {
    return this.webApp.colorScheme;
  }

  /**
   * Show Telegram WebApp alert
   */
  showAlert(message) {
    this.webApp.showAlert(message);
  }

  /**
   * Show Telegram WebApp confirm dialog
   */
  showConfirm(message, callback) {
    this.webApp.showConfirm(message, callback);
  }

  /**
   * Close Telegram WebApp
   */
  close() {
    this.webApp.close();
  }

  /**
   * Send data to bot
   */
  sendData(data) {
    this.webApp.sendData(JSON.stringify(data));
  }

  /**
   * Get main button
   */
  getMainButton() {
    return this.webApp.MainButton;
  }

  /**
   * Get back button
   */
  getBackButton() {
    return this.webApp.BackButton;
  }

  /**
   * Get haptic feedback
   */
  getHapticFeedback() {
    return this.webApp.HapticFeedback;
  }

  /**
   * Check if running in Telegram
   */
  isTelegram() {
    return this.webApp.platform !== 'unknown';
  }

  /**
   * Get platform info
   */
  getPlatform() {
    return this.webApp.platform;
  }

  /**
   * Get version
   */
  getVersion() {
    return this.webApp.version;
  }
}

// Create singleton instance
const telegramAuthService = new TelegramAuthService();

export default telegramAuthService;
