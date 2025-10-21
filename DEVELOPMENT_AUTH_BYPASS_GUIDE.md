# Development Mode Authentication Bypass Guide

## Overview
This guide explains how to bypass authentication protection for development mode to fetch balance and other protected resources.

## Current Setup
Your application has the following development flags in `.env`:
- `REACT_APP_DEV_MODE=true` - Enables development mode
- `REACT_APP_BYPASS_TELEGRAM_AUTH=true` - Bypasses Telegram authentication
- `REACT_APP_USE_MOCK_BALANCE=false` - Uses real API instead of mock data

## Solutions Implemented

### Solution 1: Development-Only Public Endpoint ✅
**Backend**: Added `/wallet/dev/player/{telegram_id}` endpoint that bypasses authentication
**Frontend**: Automatically uses dev endpoint when in development mode

**How it works:**
- Backend checks `settings.DEBUG` to ensure it's only available in development
- Frontend detects dev mode and uses the `/dev/` endpoint
- No authentication token required

**Usage:**
```javascript
// Automatically handled by walletApi.getPlayerWalletByTelegram()
// Uses /wallet/dev/player/123456789 in dev mode
// Uses /wallet/player/123456789 in production
```

### Solution 2: Smart Auth Interceptor ✅
**Frontend**: Modified API client to skip authentication for dev endpoints

**How it works:**
- Checks if request is to a `/dev/` endpoint
- Skips adding Authorization header for dev requests
- Maintains security for production endpoints

### Solution 3: Mock Balance Service ✅
**Frontend**: Created mock service for completely offline development

**How it works:**
- Returns hardcoded balance data when `REACT_APP_USE_MOCK_BALANCE=true`
- Useful for UI development without backend dependency
- Can be toggled via environment variable

**Usage:**
```javascript
// Set in .env
REACT_APP_USE_MOCK_BALANCE=true

// Returns mock data:
{
  balance: 1000.00,
  referral_bonus: 50.00,
  total_balance: 1050.00,
  dev_mode: true,
  mock: true
}
```

### Solution 4: Development Configuration ✅
**Frontend**: Centralized dev configuration for easy management

**Features:**
- Centralized development flags
- Mock user and balance data
- Smart endpoint selection
- Authentication bypass logic

## Environment Variables

### Required for Development
```bash
# Enable development mode
REACT_APP_DEV_MODE=true

# Bypass Telegram authentication
REACT_APP_BYPASS_TELEGRAM_AUTH=true

# Optional: Use mock balance instead of real API
REACT_APP_USE_MOCK_BALANCE=false
```

### Production Settings
```bash
# Disable development mode
REACT_APP_DEV_MODE=false

# Require Telegram authentication
REACT_APP_BYPASS_TELEGRAM_AUTH=false

# Always use real API
REACT_APP_USE_MOCK_BALANCE=false
```

## API Endpoints

### Development Endpoints (No Auth Required)
- `GET /api/v1/wallet/dev/player/{telegram_id}` - Get balance without auth
- Only available when `DEBUG=True` in Django settings

### Production Endpoints (Auth Required)
- `GET /api/v1/wallet/player/{telegram_id}` - Get balance with JWT auth
- `GET /api/v1/users/telegram-auth` - Telegram authentication
- `POST /api/v1/users/telegram-register` - User registration

## Testing the Solutions

### Test 1: Development Endpoint
```bash
# Start Django server
cd app
python manage.py runserver

# Test dev endpoint (should work without auth)
curl http://localhost:8000/api/v1/wallet/dev/player/123456789

# Test production endpoint (should require auth)
curl http://localhost:8000/api/v1/wallet/player/123456789
```

### Test 2: Frontend Development
```bash
# Start React app
cd bingo
npm start

# Check browser console for:
# [WalletApi] Using dev endpoint (no auth required): wallet/dev/player/123456789
# [DevWallet] user = <User object>
# [DevWallet] referral_bonus = 50.0
```

### Test 3: Mock Balance Service
```bash
# Set in .env
REACT_APP_USE_MOCK_BALANCE=true

# Restart React app
npm start

# Check browser console for:
# [MockBalance] Returning mock balance for telegram_id: 123456789
```

## Debugging

### Check Development Mode
```javascript
console.log('Dev Mode:', process.env.REACT_APP_DEV_MODE);
console.log('Bypass Auth:', process.env.REACT_APP_BYPASS_TELEGRAM_AUTH);
console.log('Use Mock:', process.env.REACT_APP_USE_MOCK_BALANCE);
```

### Check API Endpoints
```javascript
// In browser console
console.log('API Base URL:', process.env.REACT_APP_API_URL);
console.log('Current endpoint:', walletApi.getPlayerWalletByTelegram(123456789));
```

### Check Backend Debug Mode
```python
# In Django shell
from django.conf import settings
print('DEBUG mode:', settings.DEBUG)
```

## Security Considerations

### Development Mode Security
- Dev endpoints only work when `DEBUG=True`
- Mock data is clearly marked with `dev_mode: true`
- Production builds automatically disable dev features

### Production Security
- All endpoints require proper authentication
- No dev endpoints available
- JWT tokens validated on every request

## Troubleshooting

### Issue: Still getting 401 Unauthorized
**Solution**: Check that `REACT_APP_DEV_MODE=true` and `REACT_APP_BYPASS_TELEGRAM_AUTH=true`

### Issue: Dev endpoint returns 403 Forbidden
**Solution**: Ensure Django `DEBUG=True` in settings

### Issue: Mock balance not working
**Solution**: Set `REACT_APP_USE_MOCK_BALANCE=true` and restart React app

### Issue: Balance shows "NA"
**Solution**: Check browser console for API errors and verify telegram_id exists in database

## Best Practices

1. **Always use environment variables** for development flags
2. **Never commit production secrets** to version control
3. **Test both dev and production modes** before deployment
4. **Use mock data** for UI development when backend is unavailable
5. **Monitor console logs** for authentication bypass confirmations

## File Structure
```
bingo/src/
├── services/
│   ├── apiClient.js          # Main API client with dev logic
│   └── mockBalanceService.js # Mock balance service
├── config/
│   └── devConfig.js          # Development configuration
└── screens/
    └── selections.js         # Updated to use dev services

app/
├── wallet/
│   └── api.py               # Added dev endpoint
└── core/
    └── main.py             # Global auth configuration
```

This setup provides multiple layers of development convenience while maintaining production security.
