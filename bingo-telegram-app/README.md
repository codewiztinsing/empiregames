# Empire Bingo - Telegram Mini App

A React-based Telegram Mini App for playing Bingo games with real money betting.

## Features

- 🎯 **Bingo Game**: Classic 5x5 bingo with random number generation
- 💰 **Real Money Betting**: Place bets and win real money
- 👤 **User Authentication**: Telegram-based user authentication
- 💳 **Wallet System**: Deposit, withdraw, and manage funds
- 📱 **Mobile Optimized**: Designed for Telegram mobile app
- 🎨 **Modern UI**: Beautiful gradient design with animations

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Telegram Integration**: @twa-dev/sdk
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Backend**: Django REST API

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
REACT_APP_TELEGRAM_WEBAPP_URL=https://your-domain.com
```

### 3. Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

## Telegram Bot Setup

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Set up the bot menu with `/setmenu`

### 2. Configure Web App

1. Use `/newapp` command with BotFather
2. Provide your bot token
3. Set the Web App URL to your deployed app
4. Configure the app settings

### 3. Bot Commands

```
/start - Start the bingo game
/play - Play bingo
/wallet - View wallet
/profile - View profile
```

## API Integration

The app connects to your Django backend API:

### User Endpoints
- `GET /api/v1/users/telegram/{telegram_id}` - Get user by Telegram ID
- `POST /api/v1/users/register` - Register new user
- `PUT /api/v1/users/{id}` - Update user info

### Game Endpoints
- `POST /api/v1/games/create` - Create new game
- `GET /api/v1/games/{id}` - Get game details
- `POST /api/v1/games/{id}/join` - Join game

### Wallet Endpoints
- `GET /api/v1/wallet/player/{user_id}` - Get wallet balance
- `POST /api/v1/wallet/deposit` - Process deposit
- `POST /api/v1/wallet/withdraw` - Process withdrawal

## Game Features

### Bingo Game
- 5x5 bingo card with free center space
- Random number generation (1-75)
- Real-time number calling
- Automatic bingo detection
- Win/lose tracking

### Betting System
- Multiple bet amounts (10, 25, 50, 100, 200, 500 ETB)
- Custom bet amounts
- Balance validation
- Real-time balance updates

### User Management
- Telegram-based authentication
- Profile management
- Phone number collection
- Game statistics

## Deployment

### 1. Build the App

```bash
npm run build
```

### 2. Deploy to Hosting

Deploy the `build` folder to your hosting provider:

- **Netlify**: Drag and drop the build folder
- **Vercel**: Connect your GitHub repository
- **GitHub Pages**: Use GitHub Actions
- **AWS S3**: Upload build files to S3 bucket

### 3. Update Telegram Bot

1. Update the Web App URL in BotFather
2. Test the app in Telegram
3. Configure domain settings

## Development

### Project Structure

```
src/
├── components/
│   ├── Home.tsx           # Main dashboard
│   ├── BingoGame.tsx      # Bingo game component
│   ├── Profile.tsx        # User profile
│   ├── Wallet.tsx         # Wallet management
│   └── Loading.tsx        # Loading component
├── App.tsx                # Main app component
├── App.css                # Global styles
└── index.tsx              # App entry point
```

### Key Components

- **Home**: Dashboard with balance, stats, and quick actions
- **BingoGame**: Full bingo game with betting and number calling
- **Profile**: User profile management and statistics
- **Wallet**: Deposit, withdraw, and transaction history

## Security Considerations

- All API calls use HTTPS
- User authentication via Telegram
- Balance validation on client and server
- Secure payment processing
- Input validation and sanitization

## Support

For support and questions:
- Telegram: @empiregames_support
- Email: support@empiregames.com

## License

This project is proprietary software. All rights reserved.