# Empire Games Web Bot - Professional Deployment Guide

This guide provides professional deployment options for the Empire Games Web Bot (`webbot.py`) using PM2, systemd, and other production-ready tools for production server at `/var/www/empiregames`.

## 🚀 Quick Start

### Production Deployment (Recommended)

```bash
# Copy files to production server
sudo cp -r /path/to/app/files /var/www/empiregames/app/

# Run full production deployment
sudo /var/www/empiregames/app/deploy_webbot_production.sh deploy
```

### Option 1: PM2 Script

```bash
# Make script executable
chmod +x /var/www/empiregames/app/run_webbot.sh

# Start the bot
sudo /var/www/empiregames/app/run_webbot.sh start

# View logs
sudo /var/www/empiregames/app/run_webbot.sh logs

# Monitor
sudo /var/www/empiregames/app/run_webbot.sh monitor
```

### Option 2: PM2 Ecosystem File

```bash
# Start with ecosystem file
cd /var/www/empiregames/app
sudo pm2 start webbot_ecosystem.config.js

# Or start specific app
sudo pm2 start webbot_ecosystem.config.js --only empire-webbot
```

### Option 3: Systemd Service

```bash
# Copy service file
sudo cp /var/www/empiregames/app/empire-webbot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable empire-webbot
sudo systemctl start empire-webbot

# Check status
sudo systemctl status empire-webbot
```

## 📋 Prerequisites

1. **Python 3.8+** with virtual environment
2. **PM2** (Node.js process manager)
3. **Django** application running
4. **Bot Token** configured
5. **Celery** (if using async tasks)

### Install PM2

```bash
# Install PM2 globally
npm install -g pm2

# Or install via package manager
sudo apt install pm2  # Ubuntu/Debian
```

## 🔧 Configuration

### 1. Environment Variables

Create `config.env` file in `/var/www/empiregames/app/`:

```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Django Settings
DJANGO_SETTINGS_MODULE=core.settings

# Database (if needed)
DATABASE_URL=postgresql://user:password@localhost/empiregames

# Redis (if using Celery)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
```

### 2. Directory Structure

```
/var/www/empiregames/
├── app/
│   ├── webbot.py
│   ├── config.env
│   ├── run_webbot.sh
│   ├── deploy_webbot_production.sh
│   ├── webbot_ecosystem.config.js
│   ├── empire-webbot.service
│   ├── requirements.txt
│   └── venv/
└── logs/
    ├── webbot.log
    ├── webbot-out.log
    └── webbot-error.log
```

## 🛠️ Management Commands

### PM2 Script Commands

```bash
sudo /var/www/empiregames/app/run_webbot.sh start      # Start the bot
sudo /var/www/empiregames/app/run_webbot.sh stop       # Stop the bot
sudo /var/www/empiregames/app/run_webbot.sh restart    # Restart the bot
sudo /var/www/empiregames/app/run_webbot.sh status     # Show status
sudo /var/www/empiregames/app/run_webbot.sh logs       # Show logs
sudo /var/www/empiregames/app/run_webbot.sh tail       # Real-time logs
sudo /var/www/empiregames/app/run_webbot.sh monitor    # PM2 dashboard
sudo /var/www/empiregames/app/run_webbot.sh save       # Save PM2 config
sudo /var/www/empiregames/app/run_webbot.sh setup     # Setup startup script
sudo /var/www/empiregames/app/run_webbot.sh clean      # Clean logs
sudo /var/www/empiregames/app/run_webbot.sh install    # Install dependencies
```

### Production Deployment Commands

```bash
sudo /var/www/empiregames/app/deploy_webbot_production.sh deploy    # Full deployment
sudo /var/www/empiregames/app/deploy_webbot_production.sh start     # Start bot
sudo /var/www/empiregames/app/deploy_webbot_production.sh stop      # Stop bot
sudo /var/www/empiregames/app/deploy_webbot_production.sh restart   # Restart bot
sudo /var/www/empiregames/app/deploy_webbot_production.sh status    # Show status
sudo /var/www/empiregames/app/deploy_webbot_production.sh logs      # Show logs
sudo /var/www/empiregames/app/deploy_webbot_production.sh monitor   # Monitor health
```

### Direct PM2 Commands

```bash
# Basic PM2 commands
pm2 start webbot.py --name empire-webbot
pm2 stop empire-webbot
pm2 restart empire-webbot
pm2 delete empire-webbot
pm2 status
pm2 logs empire-webbot
pm2 monit

# With ecosystem file
pm2 start webbot_ecosystem.config.js
pm2 restart webbot_ecosystem.config.js
pm2 stop webbot_ecosystem.config.js
pm2 delete webbot_ecosystem.config.js
```

### Systemd Commands

```bash
# Service management
sudo systemctl start empire-webbot
sudo systemctl stop empire-webbot
sudo systemctl restart empire-webbot
sudo systemctl status empire-webbot
sudo systemctl enable empire-webbot
sudo systemctl disable empire-webbot

# View logs
sudo journalctl -u empire-webbot -f
sudo journalctl -u empire-webbot --since "1 hour ago"
```

## 📊 Monitoring & Logging

### PM2 Monitoring

```bash
# Real-time monitoring
pm2 monit

# Process information
pm2 show empire-webbot

# Log management
pm2 logs empire-webbot --lines 100
pm2 flush empire-webbot  # Clear logs
```

### Log Files

- **Main Log**: `/var/www/empiregames/logs/webbot.log`
- **Output Log**: `/var/www/empiregames/logs/webbot-out.log`
- **Error Log**: `/var/www/empiregames/logs/webbot-error.log`

### Log Rotation

Add to `/etc/logrotate.d/empire-webbot`:

```
/var/www/empiregames/logs/webbot*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        pm2 reload empire-webbot
    endscript
}
```

## 🔒 Security & Production

### 1. User Permissions

```bash
# Set ownership to www-data
sudo chown -R www-data:www-data /var/www/empiregames/app
sudo chown -R www-data:www-data /var/www/empiregames/logs
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. SSL/TLS (if using webhooks)

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com
```

## 🚨 Troubleshooting

### Common Issues

1. **Bot not starting**
   ```bash
   # Check logs
   pm2 logs empire-webbot
   
   # Check Python environment
   source /var/www/empiregames/app/venv/bin/activate
   python webbot.py
   ```

2. **Permission errors**
   ```bash
   # Fix permissions
   chmod +x run_webbot.sh
   chown -R www-data:www-data /var/www/empiregames/logs
   ```

3. **Django connection issues**
   ```bash
   # Check Django settings
   cd /var/www/empiregames/app
   python manage.py check
   ```

4. **Token issues**
   ```bash
   # Check token configuration
   cat /var/www/empiregames/app/config.env
   
   # Test token
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
   ```

### Debug Mode

```bash
# Run in debug mode
pm2 start webbot.py --name empire-webbot-debug --interpreter /var/www/empiregames/app/venv/bin/python --env DEBUG=true
```

## 📈 Performance Optimization

### 1. Memory Management

```bash
# Set memory limits
pm2 start webbot_ecosystem.config.js --max-memory-restart 500M
```

### 2. CPU Optimization

```bash
# Set CPU limits
pm2 start webbot_ecosystem.config.js --max-cpu-restart 80
```

### 3. Process Clustering

```bash
# Run multiple instances
pm2 start webbot_ecosystem.config.js --instances 2
```

## 🔄 Auto-Startup

### PM2 Startup

```bash
# Generate startup script
pm2 startup

# Save current processes
pm2 save
```

### Systemd Startup

```bash
# Enable service
sudo systemctl enable empire-webbot
```

## 📝 Maintenance

### Regular Tasks

1. **Log Rotation**: Weekly
2. **Dependency Updates**: Monthly
3. **Security Updates**: As needed
4. **Backup Configuration**: Daily

### Health Checks

```bash
# Check bot status
sudo /var/www/empiregames/app/deploy_webbot_production.sh status

# Check system resources
pm2 monit

# Check logs for errors
grep -i error /var/www/empiregames/logs/webbot-error.log
```

## 🆘 Support

For issues and support:

1. Check logs first
2. Verify configuration
3. Test in debug mode
4. Check Django application status
5. Verify network connectivity
6. Check bot token validity

## 📚 Additional Resources

- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Systemd Documentation](https://systemd.io/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 🔧 Bot-Specific Features

### Web Bot Commands

The Web Bot includes various commands for user management, transactions, and game operations:

- **User Registration**: `/start`, `/register`
- **Wallet Management**: `/balance`, `/deposit`, `/withdraw`
- **Game Operations**: `/play`, `/join`, `/leave`
- **Admin Commands**: `/admin`, `/stats`, `/users`
- **Support**: `/help`, `/support`

### Integration with Django

The Web Bot integrates with Django models:
- **User Management**: `users.models.User`
- **Transactions**: `wallet.models.Transaction`
- **Game Data**: `game.models.*`
- **Referrals**: `referrals.models.*`

### Celery Integration

If using Celery for async tasks:
```bash
# Start Celery worker
celery -A core worker --loglevel=info

# Start Celery beat (scheduler)
celery -A core beat --loglevel=info
```
