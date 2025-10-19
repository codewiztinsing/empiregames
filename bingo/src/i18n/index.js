// i18n configuration for Liyu Bingo React frontend
// src/i18n/index.js

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import en from './locales/en.json';
import am from './locales/am.json';
import om from './locales/om.json';
import so from './locales/so.json';
import ti from './locales/ti.json';

const resources = {
  en: {
    translation: en
  },
  am: {
    translation: am
  },
  om: {
    translation: om
  },
  so: {
    translation: so
  },
  ti: {
    translation: ti
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // React already does escaping
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    
    react: {
      useSuspense: false,
    }
  });

export default i18n;
