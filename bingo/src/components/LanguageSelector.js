// Language Selector Component
// src/components/LanguageSelector.js

import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSelector.css';

const LanguageSelector = () => {
  const { i18n, t } = useTranslation();

  const languages = [
    { code: 'en', name: t('languages.english'), flag: '🇺🇸' },
    { code: 'am', name: t('languages.amharic'), flag: '🇪🇹' },
    { code: 'om', name: t('languages.oromo'), flag: '🇪🇹' },
    { code: 'so', name: t('languages.somali'), flag: '🇸🇴' },
    { code: 'ti', name: t('languages.tigrinya'), flag: '🇪🇹' }
  ];

  const changeLanguage = (languageCode) => {
    i18n.changeLanguage(languageCode);
    localStorage.setItem('selectedLanguage', languageCode);
  };

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  return (
    <div className="language-selector">
      <div className="language-dropdown">
        <button className="language-button">
          <span className="flag">{currentLanguage.flag}</span>
          <span className="language-name">{currentLanguage.name}</span>
          <span className="dropdown-arrow">▼</span>
        </button>
        <div className="language-menu">
          {languages.map((language) => (
            <button
              key={language.code}
              className={`language-option ${i18n.language === language.code ? 'active' : ''}`}
              onClick={() => changeLanguage(language.code)}
            >
              <span className="flag">{language.flag}</span>
              <span className="language-name">{language.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LanguageSelector;
