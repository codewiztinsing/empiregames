# React Frontend Localization Guide

## Overview
This guide covers the React frontend localization setup for Liyu Bingo, supporting all languages from the Telegram bot: English, Amharic, Oromo, Somali, and Tigrinya.

## Features

### Supported Languages
- **English (en)** - Default language
- **Amharic (am)** - አማርኛ
- **Oromo (om)** - Afaan Oromoo  
- **Somali (so)** - Soomaali
- **Tigrinya (ti)** - ትግርኛ

### Key Features
- **Automatic language detection** from browser settings
- **Persistent language selection** stored in localStorage
- **RTL support** for future Arabic/Hebrew languages
- **Currency formatting** with local symbols
- **Date and number formatting** based on locale
- **Language selector component** with flags
- **Context-based translations** for easy access

## Installation

### Dependencies
```bash
npm install react-i18next i18next i18next-browser-languagedetector i18next-http-backend --legacy-peer-deps
```

### Package Versions
- `react-i18next`: Latest
- `i18next`: Latest  
- `i18next-browser-languagedetector`: Latest
- `i18next-http-backend`: Latest

## File Structure

```
src/
├── i18n/
│   ├── index.js                 # i18n configuration
│   └── locales/
│       ├── en.json             # English translations
│       ├── am.json             # Amharic translations
│       ├── om.json             # Oromo translations
│       ├── so.json             # Somali translations
│       └── ti.json             # Tigrinya translations
├── components/
│   ├── LanguageSelector.js      # Language selector component
│   └── LanguageSelector.css     # Language selector styles
├── contexts/
│   └── LocalizationContext.js  # Localization context provider
└── hooks/
    └── useTranslation.js       # Custom translation hook
```

## Usage

### Basic Translation
```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('game.welcome')}</h1>
      <p>{t('game.selectCard')}</p>
    </div>
  );
}
```

### Using Custom Hook
```jsx
import { useTranslation } from './hooks/useTranslation';

function MyComponent() {
  const { t, formatCurrency, formatNumber, formatDate } = useTranslation();
  
  return (
    <div>
      <h1>{t('game.welcome')}</h1>
      <p>Balance: {formatCurrency(1000)}</p>
      <p>Players: {formatNumber(150)}</p>
      <p>Date: {formatDate(new Date())}</p>
    </div>
  );
}
```

### Using Localization Context
```jsx
import { useLocalization } from './contexts/LocalizationContext';

function MyComponent() {
  const { 
    currentLanguage, 
    changeLanguage, 
    formatCurrency,
    getAvailableLanguages 
  } = useLocalization();
  
  return (
    <div>
      <p>Current language: {currentLanguage}</p>
      <button onClick={() => changeLanguage('am')}>
        Switch to Amharic
      </button>
    </div>
  );
}
```

### Language Selector Component
```jsx
import LanguageSelector from './components/LanguageSelector';

function Header() {
  return (
    <header>
      <h1>Liyu Bingo</h1>
      <LanguageSelector />
    </header>
  );
}
```

## Translation Keys Structure

### Common Keys
```json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "cancel": "Cancel",
    "confirm": "Confirm"
  }
}
```

### Game Keys
```json
{
  "game": {
    "welcome": "Welcome to Liyu Bingo!",
    "selectCard": "Select Your Card",
    "balance": "Balance",
    "totalPlayers": "Total Players"
  }
}
```

### Navigation Keys
```json
{
  "navigation": {
    "home": "Home",
    "play": "Play",
    "profile": "Profile",
    "settings": "Settings"
  }
}
```

## Adding New Translations

### 1. Add New Keys
Add new translation keys to all language files:

**en.json**
```json
{
  "newFeature": {
    "title": "New Feature",
    "description": "This is a new feature"
  }
}
```

**am.json**
```json
{
  "newFeature": {
    "title": "ባህሪ ሐዲስ",
    "description": "እዚ ባህሪ ሐዲስ እዩ"
  }
}
```

### 2. Use in Components
```jsx
const { t } = useTranslation();
return <h2>{t('newFeature.title')}</h2>;
```

## Language Detection

### Automatic Detection Order
1. **localStorage** - Previously selected language
2. **navigator** - Browser language settings
3. **htmlTag** - HTML lang attribute
4. **fallback** - English (en)

### Manual Language Change
```jsx
const { changeLanguage } = useLocalization();

// Change to Amharic
changeLanguage('am');

// Change to Oromo
changeLanguage('om');
```

## Formatting Functions

### Currency Formatting
```jsx
const { formatCurrency } = useTranslation();

// Ethiopian Birr
formatCurrency(1000); // "Br1,000"

// With custom currency
formatCurrency(1000, 'USD'); // "$1,000"
```

### Number Formatting
```jsx
const { formatNumber } = useTranslation();

formatNumber(1234567); // "1,234,567" (English)
formatNumber(1234567); // "1,234,567" (Amharic)
```

### Date Formatting
```jsx
const { formatDate } = useTranslation();

formatDate(new Date()); // "January 1, 2024 at 12:00 PM"
formatDate(new Date(), { dateStyle: 'short' }); // "1/1/2024"
```

## RTL Support

### Current Implementation
- **Direction detection** for future RTL languages
- **CSS classes** for RTL styling
- **Context-aware** direction handling

### Adding RTL Language
```jsx
// In LocalizationContext.js
const getDirection = (languageCode) => {
  const rtlLanguages = ['ar', 'he', 'fa', 'ur']; // Add new RTL language
  return rtlLanguages.includes(languageCode) ? 'rtl' : 'ltr';
};
```

## Best Practices

### 1. Translation Keys
- Use **descriptive names** for keys
- **Group related keys** in objects
- **Keep keys consistent** across languages
- **Use interpolation** for dynamic content

### 2. Component Structure
```jsx
// Good
const { t } = useTranslation();
return <h1>{t('game.welcome')}</h1>;

// Avoid
return <h1>Welcome to Liyu Bingo!</h1>;
```

### 3. Pluralization
```json
{
  "items": {
    "zero": "No items",
    "one": "One item", 
    "other": "{{count}} items"
  }
}
```

```jsx
const { t } = useTranslation();
return <p>{t('items', { count: 5 })}</p>; // "5 items"
```

### 4. Interpolation
```json
{
  "welcome": "Welcome {{name}}!"
}
```

```jsx
const { t } = useTranslation();
return <h1>{t('welcome', { name: 'John' })}</h1>;
```

## Testing

### Language Switching Test
```jsx
import { render, screen } from '@testing-library/react';
import { useTranslation } from 'react-i18next';

test('language switching works', () => {
  const { t } = useTranslation();
  expect(t('game.welcome')).toBe('Welcome to Liyu Bingo!');
});
```

### Component Test
```jsx
import { render, screen } from '@testing-library/react';
import LanguageSelector from './components/LanguageSelector';

test('language selector renders', () => {
  render(<LanguageSelector />);
  expect(screen.getByText('English')).toBeInTheDocument();
});
```

## Performance Optimization

### 1. Lazy Loading
```jsx
// Load translations on demand
const loadTranslations = async (language) => {
  const translations = await import(`./locales/${language}.json`);
  i18n.addResourceBundle(language, 'translation', translations.default);
};
```

### 2. Namespace Separation
```jsx
// Separate namespaces for different features
i18n.loadNamespaces(['game', 'auth', 'profile']);
```

### 3. Caching
```jsx
// Cache translations in localStorage
const cacheTranslations = (language, translations) => {
  localStorage.setItem(`translations_${language}`, JSON.stringify(translations));
};
```

## Troubleshooting

### Common Issues

1. **Translation not found**
   ```jsx
   // Check if key exists in all language files
   console.log(t('missing.key')); // Shows "missing.key" if not found
   ```

2. **Language not switching**
   ```jsx
   // Ensure i18n is properly initialized
   import './i18n';
   ```

3. **Formatting not working**
   ```jsx
   // Check if locale is supported
   const supportedLocales = ['en', 'am', 'om', 'so', 'ti'];
   ```

### Debug Mode
```jsx
// Enable debug mode in development
i18n.init({
  debug: process.env.NODE_ENV === 'development'
});
```

## Integration with Telegram Bot

### Language Synchronization
The React frontend uses the same language codes as the Telegram bot:

- **English**: `en`
- **Amharic**: `am` 
- **Oromo**: `om`
- **Somali**: `so`
- **Tigrinya**: `ti`

### API Integration
```jsx
// Send language preference to backend
const updateLanguagePreference = async (language) => {
  await api.post('/user/language', { language });
};
```

This localization setup provides a comprehensive multi-language experience for the Liyu Bingo React frontend, matching the language support in the Telegram bot.
