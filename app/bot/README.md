# Standalone Agent Bot

A Telegram bot for managing agents and their referrals independently from the main bot.

## Features

- **Agent Registration**: Users can register as agents and get unique invite codes
- **Player Referral System**: Players can join via agent invite links
- **Commission Tracking**: Agents earn commission when their players deposit ≥100 Birr
- **Statistics**: View detailed stats for agents and players
- **In-Memory Storage**: Uses in-memory storage (can be replaced with database)

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install python-telegram-bot python-decouple
   ```

2. **Configure Bot**:
   ```bash
   cp config.env.example config.env
   # Edit config.env and add your bot token
   ```

3. **Run the Bot**:
   ```bash
   python start_bot.py
   ```

## Bot Commands

### For Everyone
- `/start` - Start the bot
- `/help` - Show help message
- `/my_stats` - View your statistics

### For Agents
- `/register_agent` - Register as an agent
- `/agent_menu` - Open agent menu

### Testing
- `/deposit <amount>` - Simulate a deposit (for testing)

## How It Works

1. **Agent Registration**: Users use `/register_agent` to become agents
2. **Invite Links**: Agents get unique invite links to share
3. **Player Joining**: Players use invite links to join
4. **Commission**: Agents earn 1 Birr for each player deposit ≥100 Birr
5. **Statistics**: Both agents and players can view their stats

## Configuration

Edit `config.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
LOG_LEVEL=INFO
```

## Database Integration

To use persistent storage instead of in-memory:

1. Install database driver (e.g., `pip install psycopg2-binary` for PostgreSQL)
2. Update `config.env` with database URL
3. Modify `standalone_agent_bot.py` to use database instead of dictionaries

## File Structure

```
app/bot/
├── standalone_agent_bot.py  # Main bot code
├── start_bot.py            # Startup script
├── config.env.example      # Configuration template
└── README.md              # This file
```

## Development

The bot is designed to be easily extensible:

- Add new commands by creating handler methods
- Modify commission logic in `record_deposit()`
- Add database integration for persistent storage
- Extend statistics and reporting features

## Security Notes

- Keep your bot token secure
- Consider rate limiting for production use
- Add input validation for user commands
- Implement proper error handling for production
