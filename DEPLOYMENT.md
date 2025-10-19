# Liyu Bingo Telegram Bot - Production Deployment Guide

## Overview
This guide covers multiple ways to deploy the Liyu Bingo Telegram Bot in production.

## Prerequisites
- Ubuntu 20.04+ server
- Python 3.11+
- PostgreSQL (optional, can use SQLite)
- Redis (optional, for caching)
- Domain name with SSL certificate
- Telegram Bot Token from @BotFather

## Method 1: Systemd Service (Recommended)

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev postgresql postgresql-contrib redis-server nginx -y

# Create project directory
sudo mkdir -p /opt/liyu-bot
sudo chown $USER:$USER /opt/liyu-bot
```

### 2. Deploy Application
```bash
# Clone/copy your project
cd /opt/liyu-bot
git clone <your-repo> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install python-telegram-bot python-decouple requests

# Copy environment file
cp production.env.example .env.production
# Edit .env.production with your actual values
```

### 3. Configure Environment
```bash
# Edit .env.production
nano .env.production

# Required values:
BOT_TOKEN=your-telegram-bot-token
BACK_URL=https://yourdomain.com
DJANGO_SECRET_KEY=your-secret-key
MANUAL_API_KEY=your-manual-api-key
MANUAL_BASE_URL=https://your-manual-api.com/
```

### 4. Setup Database
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Install Systemd Service
```bash
# Copy service file
sudo cp liyu-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable liyu-bot
sudo systemctl start liyu-bot

# Check status
sudo systemctl status liyu-bot
```

### 6. Setup Logging
```bash
# Create log directory
sudo mkdir -p /var/log/liyu-bot
sudo chown $USER:$USER /var/log/liyu-bot

# View logs
sudo journalctl -u liyu-bot -f
```

## Method 2: Docker Deployment

### 1. Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

### 2. Configure Environment
```bash
# Copy environment file
cp production.env.example .env

# Edit with your values
nano .env
```

### 3. Deploy with Docker Compose
```bash
# Start services
docker-compose -f docker-compose.bot.yml up -d

# View logs
docker-compose -f docker-compose.bot.yml logs -f liyu-bot

# Stop services
docker-compose -f docker-compose.bot.yml down
```

## Method 3: Using Bot Runner Script

### 1. Setup
```bash
# Make script executable
chmod +x bot-runner.sh

# Install dependencies
./bot-runner.sh install

# Start bot
./bot-runner.sh start

# Check status
./bot-runner.sh status

# View logs
./bot-runner.sh logs

# Stop bot
./bot-runner.sh stop
```

## Nginx Configuration (Optional)

### 1. Create Nginx Config
```nginx
# /etc/nginx/sites-available/liyu-bot
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/liyu-bot/staticfiles/;
    }

    location /media/ {
        alias /opt/liyu-bot/media/;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/liyu-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Check bot status
sudo systemctl status liyu-bot

# Check logs
sudo journalctl -u liyu-bot -f

# Check database
python manage.py check --deploy
```

### 2. Backup
```bash
# Backup database
pg_dump liyu_bingo > backup_$(date +%Y%m%d).sql

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 3. Updates
```bash
# Stop bot
sudo systemctl stop liyu-bot

# Update code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Restart bot
sudo systemctl start liyu-bot
```

## Troubleshooting

### Common Issues

1. **Bot not starting**
   ```bash
   # Check logs
   sudo journalctl -u liyu-bot -n 50
   
   # Check environment variables
   sudo systemctl show liyu-bot --property=Environment
   ```

2. **Database connection issues**
   ```bash
   # Test database connection
   python manage.py dbshell
   
   # Check database status
   sudo systemctl status postgresql
   ```

3. **Permission issues**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER /opt/liyu-bot
   
   # Fix log permissions
   sudo chown -R $USER:$USER /var/log/liyu-bot
   ```

### Performance Optimization

1. **Enable Redis caching**
2. **Use PostgreSQL instead of SQLite**
3. **Configure log rotation**
4. **Monitor memory usage**

## Security Considerations

1. **Use environment variables for secrets**
2. **Enable SSL/TLS**
3. **Configure firewall**
4. **Regular security updates**
5. **Monitor logs for suspicious activity**

## Scaling

For high-traffic scenarios:
1. **Use load balancer**
2. **Multiple bot instances**
3. **Database clustering**
4. **Redis cluster**
5. **CDN for static files**

## Support

For issues and support:
- Check logs: `sudo journalctl -u liyu-bot -f`
- Bot status: `sudo systemctl status liyu-bot`
- Django checks: `python manage.py check --deploy`
