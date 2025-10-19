// Localization Context Provider
// src/contexts/LocalizationContext.js

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const LocalizationContext = createContext();

export const useLocalization = () => {
  const context = useContext(LocalizationContext);
  if (!context) {
    throw new Error('useLocalization must be used within a LocalizationProvider');
  }
  return context;
};

export const LocalizationProvider = ({ children }) => {
  const { i18n, t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);

  const getDirection = (languageCode) => {
    const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
    return rtlLanguages.includes(languageCode) ? 'rtl' : 'ltr';
  };

  const changeLanguage = async (languageCode) => {
    setIsLoading(true);
    try {
      await i18n.changeLanguage(languageCode);
      localStorage.setItem('selectedLanguage', languageCode);
      setCurrentLanguage(languageCode);
    } catch (error) {
      console.error('Error changing language:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Load saved language preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('selectedLanguage');
    if (savedLanguage && savedLanguage !== i18n.language) {
      changeLanguage(savedLanguage);
    }
  }, [i18n.language]);

  // Listen for language changes
  useEffect(() => {
    const handleLanguageChange = (lng) => {
      setCurrentLanguage(lng);
      document.documentElement.lang = lng;
      document.documentElement.dir = getDirection(lng);
    };

    i18n.on('languageChanged', handleLanguageChange);
    
    // Set initial language
    handleLanguageChange(i18n.language);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

  const formatCurrency = (amount, currency = 'ETB') => {
    const symbol = t('currency.symbol');
    return `${symbol}${amount.toLocaleString()}`;
  };

  const formatNumber = (number) => {
    return number.toLocaleString(currentLanguage);
  };

  const formatDate = (date, options = {}) => {
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat(currentLanguage, { ...defaultOptions, ...options }).format(new Date(date));
  };

  const isRTL = () => {
    return getDirection(currentLanguage) === 'rtl';
  };

  const getLanguageName = (code) => {
    return t(`languages.${code}`);
  };

  const getAvailableLanguages = () => {
    return [
      { code: 'en', name: t('languages.english'), flag: '🇺🇸' },
      { code: 'am', name: t('languages.amharic'), flag: '🇪🇹' },
      { code: 'om', name: t('languages.oromo'), flag: '🇪🇹' },
      { code: 'so', name: t('languages.somali'), flag: '🇸🇴' },
      { code: 'ti', name: t('languages.tigrinya'), flag: '🇪🇹' }
    ];
  };

  const value = {
    currentLanguage,
    isLoading,
    changeLanguage,
    formatCurrency,
    formatNumber,
    formatDate,
    isRTL,
    getLanguageName,
    getAvailableLanguages,
    t,
    i18n
  };

  return (
    <LocalizationContext.Provider value={value}>
      {children}
    </LocalizationContext.Provider>
  );
};
