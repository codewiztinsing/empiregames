# Empire Games Support Bot - Professional Deployment Guide

This guide provides professional deployment options for the Empire Games Support Bot using PM2, systemd, and other production-ready tools.

## 🚀 Quick Start

### Option 1: PM2 (Recommended)

```bash
# Make script executable
chmod +x run_support_bot.sh

# Start the bot
./run_support_bot.sh start

# View logs
./run_support_bot.sh logs

# Monitor
./run_support_bot.sh monitor
```

### Option 2: PM2 Ecosystem File

```bash
# Start with ecosystem file
pm2 start ecosystem.config.js

# Or start specific app
pm2 start ecosystem.config.js --only empire-support-bot
```

### Option 3: Systemd Service

```bash
# Copy service file
sudo cp empire-support-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable empire-support-bot
sudo systemctl start empire-support-bot

# Check status
sudo systemctl status empire-support-bot
```

## 📋 Prerequisites

1. **Python 3.8+** with virtual environment
2. **PM2** (Node.js process manager)
3. **Django** application running
4. **Bot Token** configured

### Install PM2

```bash
# Install PM2 globally
npm install -g pm2

# Or install via package manager
sudo apt install pm2  # Ubuntu/Debian
```

## 🔧 Configuration

### 1. Environment Variables

Create `config.env` file:

```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Django Settings
DJANGO_SETTINGS_MODULE=core.settings

# Logging
LOG_LEVEL=INFO
```

### 2. Directory Structure

```
/home/tinsae/Desktop/projects/empiregames/
├── app/
│   ├── bot/
│   │   ├── support.py
│   │   ├── config.env
│   │   ├── run_support_bot.sh
│   │   └── ecosystem.config.js
│   └── venv/
└── logs/
    ├── support-bot.log
    ├── support-bot-out.log
    └── support-bot-error.log
```

## 🛠️ Management Commands

### PM2 Script Commands

```bash
./run_support_bot.sh start      # Start the bot
./run_support_bot.sh stop       # Stop the bot
./run_support_bot.sh restart    # Restart the bot
./run_support_bot.sh status     # Show status
./run_support_bot.sh logs       # Show logs
./run_support_bot.sh tail       # Real-time logs
./run_support_bot.sh monitor    # PM2 dashboard
./run_support_bot.sh save       # Save PM2 config
./run_support_bot.sh setup      # Setup startup script
./run_support_bot.sh clean      # Clean logs
./run_support_bot.sh install    # Install dependencies
```

### Direct PM2 Commands

```bash
# Basic PM2 commands
pm2 start support.py --name empire-support-bot
pm2 stop empire-support-bot
pm2 restart empire-support-bot
pm2 delete empire-support-bot
pm2 status
pm2 logs empire-support-bot
pm2 monit

# With ecosystem file
pm2 start ecosystem.config.js
pm2 restart ecosystem.config.js
pm2 stop ecosystem.config.js
pm2 delete ecosystem.config.js
```

### Systemd Commands

```bash
# Service management
sudo systemctl start empire-support-bot
sudo systemctl stop empire-support-bot
sudo systemctl restart empire-support-bot
sudo systemctl status empire-support-bot
sudo systemctl enable empire-support-bot
sudo systemctl disable empire-support-bot

# View logs
sudo journalctl -u empire-support-bot -f
sudo journalctl -u empire-support-bot --since "1 hour ago"
```

## 📊 Monitoring & Logging

### PM2 Monitoring

```bash
# Real-time monitoring
pm2 monit

# Process information
pm2 show empire-support-bot

# Log management
pm2 logs empire-support-bot --lines 100
pm2 flush empire-support-bot  # Clear logs
```

### Log Files

- **Main Log**: `/home/tinsae/Desktop/projects/empiregames/logs/support-bot.log`
- **Output Log**: `/home/tinsae/Desktop/projects/empiregames/logs/support-bot-out.log`
- **Error Log**: `/home/tinsae/Desktop/projects/empiregames/logs/support-bot-error.log`

### Log Rotation

Add to `/etc/logrotate.d/empire-support-bot`:

```
/home/tinsae/Desktop/projects/empiregames/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 tinsae tinsae
    postrotate
        pm2 reload empire-support-bot
    endscript
}
```

## 🔒 Security & Production

### 1. User Permissions

```bash
# Create dedicated user
sudo useradd -r -s /bin/false empire-bot

# Set ownership
sudo chown -R empire-bot:empire-bot /home/tinsae/Desktop/projects/empiregames/app/bot
sudo chown -R empire-bot:empire-bot /home/tinsae/Desktop/projects/empiregames/logs
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
   pm2 logs empire-support-bot
   
   # Check Python environment
   source /home/tinsae/Desktop/projects/empiregames/app/venv/bin/activate
   python support.py
   ```

2. **Permission errors**
   ```bash
   # Fix permissions
   chmod +x run_support_bot.sh
   chown -R $USER:$USER /home/tinsae/Desktop/projects/empiregames/logs
   ```

3. **Django connection issues**
   ```bash
   # Check Django settings
   cd /home/tinsae/Desktop/projects/empiregames/app
   python manage.py check
   ```

### Debug Mode

```bash
# Run in debug mode
pm2 start support.py --name empire-support-bot-debug --interpreter /home/tinsae/Desktop/projects/empiregames/app/venv/bin/python --env DEBUG=true
```

## 📈 Performance Optimization

### 1. Memory Management

```bash
# Set memory limits
pm2 start ecosystem.config.js --max-memory-restart 500M
```

### 2. CPU Optimization

```bash
# Set CPU limits
pm2 start ecosystem.config.js --max-cpu-restart 80
```

### 3. Process Clustering

```bash
# Run multiple instances
pm2 start ecosystem.config.js --instances 2
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
sudo systemctl enable empire-support-bot
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
./run_support_bot.sh status

# Check system resources
pm2 monit

# Check logs for errors
grep -i error /home/tinsae/Desktop/projects/empiregames/logs/support-bot-error.log
```

## 🆘 Support

For issues and support:

1. Check logs first
2. Verify configuration
3. Test in debug mode
4. Check Django application status
5. Verify network connectivity

## 📚 Additional Resources

- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Systemd Documentation](https://systemd.io/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
