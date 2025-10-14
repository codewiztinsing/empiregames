// Telegram WebApp API integration
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
          start_param?: string;
        };
        version: string;
        platform: string;
        colorScheme: 'light' | 'dark';
        themeParams: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
        };
        isExpanded: boolean;
        viewportHeight: number;
        viewportStableHeight: number;
        headerColor: string;
        backgroundColor: string;
        isClosingConfirmationEnabled: boolean;
        BackButton: {
          isVisible: boolean;
          onClick: (callback: () => void) => void;
          offClick: (callback: () => void) => void;
          show: () => void;
          hide: () => void;
        };
        MainButton: {
          text: string;
          color: string;
          textColor: string;
          isVisible: boolean;
          isActive: boolean;
          isProgressVisible: boolean;
          setText: (text: string) => void;
          onClick: (callback: () => void) => void;
          offClick: (callback: () => void) => void;
          show: () => void;
          hide: () => void;
          enable: () => void;
          disable: () => void;
          showProgress: () => void;
          hideProgress: () => void;
          setParams: (params: {
            text?: string;
            color?: string;
            text_color?: string;
            is_active?: boolean;
            is_visible?: boolean;
          }) => void;
        };
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
          selectionChanged: () => void;
        };
        CloudStorage: {
          setItem: (key: string, value: string, callback?: (error: string | null, success: boolean) => void) => void;
          getItem: (key: string, callback: (error: string | null, value: string | null) => void) => void;
          getItems: (keys: string[], callback: (error: string | null, values: Record<string, string>) => void) => void;
          removeItem: (key: string, callback?: (error: string | null, success: boolean) => void) => void;
          removeItems: (keys: string[], callback?: (error: string | null, success: boolean) => void) => void;
          getKeys: (callback: (error: string | null, keys: string[]) => void) => void;
        };
        ready: () => void;
        expand: () => void;
        close: () => void;
        showAlert: (message: string, callback?: () => void) => void;
        showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
        showPopup: (params: {
          title?: string;
          message: string;
          buttons?: Array<{
            id?: string;
            type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
            text: string;
          }>;
        }, callback?: (buttonId: string) => void) => void;
        showScanQrPopup: (params: {
          text?: string;
        }, callback?: (text: string) => void) => void;
        closeScanQrPopup: () => void;
        readTextFromClipboard: (callback?: (text: string) => void) => void;
        requestWriteAccess: (callback?: (granted: boolean) => void) => void;
        requestContact: (callback?: (granted: boolean) => void) => void;
        openLink: (url: string, options?: { try_instant_view?: boolean }) => void;
        openTelegramLink: (url: string) => void;
        openInvoice: (url: string, callback?: (status: string) => void) => void;
        sendData: (data: string) => void;
        enableClosingConfirmation: () => void;
        disableClosingConfirmation: () => void;
        onEvent: (eventType: string, eventHandler: () => void) => void;
        offEvent: (eventType: string, eventHandler: () => void) => void;
      };
    };
  }
}

export const WebApp = {
  ready: () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
    }
  },
  
  expand: () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.expand();
    }
  },
  
  showAlert: (message: string, callback?: () => void) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.showAlert(message, callback);
    } else {
      window.alert(message);
      if (callback) callback();
    }
  },
  
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.showConfirm(message, callback);
    } else {
      const confirmed = window.confirm(message);
      if (callback) callback(confirmed);
    }
  },
  
  get initDataUnsafe() {
    return window.Telegram?.WebApp?.initDataUnsafe || {};
  },
  
  get user() {
    return window.Telegram?.WebApp?.initDataUnsafe?.user;
  },
  
  get themeParams() {
    return window.Telegram?.WebApp?.themeParams || {};
  },
  
  get colorScheme() {
    return window.Telegram?.WebApp?.colorScheme || 'light';
  },
  
  get platform() {
    return window.Telegram?.WebApp?.platform || 'unknown';
  },
  
  get version() {
    return window.Telegram?.WebApp?.version || 'unknown';
  },
  
  get isExpanded() {
    return window.Telegram?.WebApp?.isExpanded || false;
  },
  
  get viewportHeight() {
    return window.Telegram?.WebApp?.viewportHeight || window.innerHeight;
  },
  
  get viewportStableHeight() {
    return window.Telegram?.WebApp?.viewportStableHeight || window.innerHeight;
  },
  
  get headerColor() {
    return window.Telegram?.WebApp?.headerColor || '#000000';
  },
  
  get backgroundColor() {
    return window.Telegram?.WebApp?.backgroundColor || '#ffffff';
  },
  
  get isClosingConfirmationEnabled() {
    return window.Telegram?.WebApp?.isClosingConfirmationEnabled || false;
  },
  
  get BackButton() {
    return window.Telegram?.WebApp?.BackButton || {
      isVisible: false,
      onClick: () => {},
      offClick: () => {},
      show: () => {},
      hide: () => {},
    };
  },
  
  get MainButton() {
    return window.Telegram?.WebApp?.MainButton || {
      text: '',
      color: '#000000',
      textColor: '#ffffff',
      isVisible: false,
      isActive: true,
      isProgressVisible: false,
      setText: () => {},
      onClick: () => {},
      offClick: () => {},
      show: () => {},
      hide: () => {},
      enable: () => {},
      disable: () => {},
      showProgress: () => {},
      hideProgress: () => {},
      setParams: () => {},
    };
  },
  
  get HapticFeedback() {
    return window.Telegram?.WebApp?.HapticFeedback || {
      impactOccurred: () => {},
      notificationOccurred: () => {},
      selectionChanged: () => {},
    };
  },
  
  close: () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.close();
    }
  },
  
  openLink: (url: string, options?: { try_instant_view?: boolean }) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openLink(url, options);
    } else {
      window.open(url, '_blank');
    }
  },
  
  openTelegramLink: (url: string) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openTelegramLink(url);
    } else {
      window.open(url, '_blank');
    }
  },
  
  sendData: (data: string) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.sendData(data);
    }
  },
  
  enableClosingConfirmation: () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.enableClosingConfirmation();
    }
  },
  
  disableClosingConfirmation: () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.disableClosingConfirmation();
    }
  },
  
  onEvent: (eventType: string, eventHandler: () => void) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.onEvent(eventType, eventHandler);
    }
  },
  
  offEvent: (eventType: string, eventHandler: () => void) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.offEvent(eventType, eventHandler);
    }
  },
};

export default WebApp;
