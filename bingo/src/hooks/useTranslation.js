// Custom hook for translations with additional utilities
// src/hooks/useTranslation.js

import { useTranslation as useI18nTranslation } from 'react-i18next';

export const useTranslation = () => {
  const { t, i18n } = useI18nTranslation();

  // Helper function to format currency
  const formatCurrency = (amount, currency = 'ETB') => {
    const symbol = t('currency.symbol');
    return `${symbol}${amount.toLocaleString()}`;
  };

  // Helper function to format numbers
  const formatNumber = (number) => {
    return number.toLocaleString(i18n.language);
  };

  // Helper function to format dates
  const formatDate = (date, options = {}) => {
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat(i18n.language, { ...defaultOptions, ...options }).format(new Date(date));
  };

  // Helper function to get current language direction
  const getDirection = () => {
    const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
    return rtlLanguages.includes(i18n.language) ? 'rtl' : 'ltr';
  };

  // Helper function to check if current language is RTL
  const isRTL = () => {
    return getDirection() === 'rtl';
  };

  // Helper function to get language name
  const getLanguageName = (code) => {
    return t(`languages.${code}`);
  };

  // Helper function to get all available languages
  const getAvailableLanguages = () => {
    return [
      { code: 'en', name: t('languages.english'), flag: '🇺🇸' },
      { code: 'am', name: t('languages.amharic'), flag: '🇪🇹' },
      { code: 'om', name: t('languages.oromo'), flag: '🇪🇹' },
      { code: 'so', name: t('languages.somali'), flag: '🇸🇴' },
      { code: 'ti', name: t('languages.tigrinya'), flag: '🇪🇹' }
    ];
  };

  return {
    t,
    i18n,
    formatCurrency,
    formatNumber,
    formatDate,
    getDirection,
    isRTL,
    getLanguageName,
    getAvailableLanguages
  };
};
