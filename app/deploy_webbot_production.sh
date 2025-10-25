#!/bin/bash

# Empire Games Web Bot - Production Deployment Script
# For production server at /var/www/empiregames

set -e  # Exit on any error

# Production Configuration
BOT_NAME="empire-webbot"
BOT_DIR="/var/www/empiregames/app"
PYTHON_ENV="/var/www/empiregames/app/venv"
LOG_DIR="/var/www/empiregames/logs"
CONFIG_FILE="config.env"
WEB_USER="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root or with sudo
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root or with sudo for production deployment"
        exit 1
    fi
    log "Running with root permissions"
}

# Check if PM2 is installed
check_pm2() {
    if ! command -v pm2 &> /dev/null; then
        error "PM2 is not installed. Installing PM2..."
        npm install -g pm2
        if [ $? -eq 0 ]; then
            success "PM2 installed successfully"
        else
            error "Failed to install PM2"
            exit 1
        fi
    else
        log "PM2 is already installed"
    fi
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$PYTHON_ENV" ]; then
        error "Python virtual environment not found at $PYTHON_ENV"
        log "Creating virtual environment..."
        python3 -m venv "$PYTHON_ENV"
        success "Virtual environment created"
    fi
    log "Virtual environment found at $PYTHON_ENV"
}

# Check if config file exists
check_config() {
    if [ ! -f "$BOT_DIR/$CONFIG_FILE" ]; then
        warning "Config file $CONFIG_FILE not found. Creating from example..."
        if [ -f "$BOT_DIR/config.env.example" ]; then
            cp "$BOT_DIR/config.env.example" "$BOT_DIR/$CONFIG_FILE"
            chown $WEB_USER:$WEB_USER "$BOT_DIR/$CONFIG_FILE"
            warning "Please edit $BOT_DIR/$CONFIG_FILE with your bot token"
            exit 1
        else
            error "No config file found. Please create $BOT_DIR/$CONFIG_FILE"
            exit 1
        fi
    fi
    log "Config file found"
}

# Create directories and set permissions
setup_directories() {
    log "Setting up directories and permissions..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    chown -R $WEB_USER:$WEB_USER "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    
    # Set bot directory permissions
    chown -R $WEB_USER:$WEB_USER "$BOT_DIR"
    chmod 755 "$BOT_DIR"
    
    # Make scripts executable
    chmod +x "$BOT_DIR"/*.sh
    
    success "Directories and permissions set up"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    source "$PYTHON_ENV/bin/activate"
    pip install --upgrade pip
    pip install -r "$BOT_DIR/requirements.txt" --quiet
    success "Dependencies installed"
}

# Start the bot with PM2
start_bot() {
    log "Starting $BOT_NAME with PM2..."
    
    # Stop existing process if running
    pm2 stop "$BOT_NAME" 2>/dev/null || true
    pm2 delete "$BOT_NAME" 2>/dev/null || true
    
    # Start the bot
    cd "$BOT_DIR"
    pm2 start webbot_ecosystem.config.js
    
    if [ $? -eq 0 ]; then
        success "Web Bot started successfully!"
        log "Bot logs: $LOG_DIR/webbot.log"
        log "Error logs: $LOG_DIR/webbot-error.log"
    else
        error "Failed to start bot"
        exit 1
    fi
}

# Setup PM2 startup
setup_pm2_startup() {
    log "Setting up PM2 startup..."
    pm2 startup systemd -u $WEB_USER --hp /var/www/empiregames
    pm2 save
    success "PM2 startup configured"
}

# Setup systemd service
setup_systemd() {
    log "Setting up systemd service..."
    cp "$BOT_DIR/empire-webbot.service" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable empire-webbot
    success "Systemd service configured"
}

# Setup log rotation
setup_logrotate() {
    log "Setting up log rotation..."
    cat > /etc/logrotate.d/empire-webbot << EOF
$LOG_DIR/webbot*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $WEB_USER $WEB_USER
    postrotate
        pm2 reload $BOT_NAME
    endscript
}
EOF
    success "Log rotation configured"
}

# Create monitoring script
create_monitoring() {
    log "Creating monitoring script..."
    cat > /usr/local/bin/empire-webbot-monitor << 'EOF'
#!/bin/bash
# Empire Web Bot Health Check Script

BOT_NAME="empire-webbot"
LOG_DIR="/var/www/empiregames/logs"

# Check if bot is running
if ! pm2 list | grep -q "$BOT_NAME.*online"; then
    echo "ERROR: Web Bot is not running!"
    pm2 restart $BOT_NAME
    exit 1
fi

# Check for errors in logs
if [ -f "$LOG_DIR/webbot-error.log" ]; then
    ERROR_COUNT=$(tail -n 100 "$LOG_DIR/webbot-error.log" | grep -c "ERROR" || true)
    if [ "$ERROR_COUNT" -gt 10 ]; then
        echo "WARNING: High error count in logs: $ERROR_COUNT"
    fi
fi

echo "Web Bot health check passed"
EOF
    chmod +x /usr/local/bin/empire-webbot-monitor
    success "Monitoring script created"
}

# Setup cron job for monitoring
setup_cron() {
    log "Setting up cron job for monitoring..."
    (crontab -u $WEB_USER -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/empire-webbot-monitor") | crontab -u $WEB_USER -
    success "Cron job configured"
}

# Show status
show_status() {
    log "Web Bot status:"
    pm2 status "$BOT_NAME"
    echo ""
    log "Systemd service status:"
    systemctl status empire-webbot --no-pager
}

# Main deployment function
deploy() {
    log "Starting production deployment for Web Bot..."
    
    check_permissions
    check_pm2
    check_venv
    check_config
    setup_directories
    install_dependencies
    start_bot
    setup_pm2_startup
    setup_systemd
    setup_logrotate
    create_monitoring
    setup_cron
    
    success "Production deployment completed!"
    show_status
}

# Show help
show_help() {
    echo "Empire Games Web Bot - Production Deployment"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy      Full production deployment"
    echo "  start       Start the bot"
    echo "  stop        Stop the bot"
    echo "  restart     Restart the bot"
    echo "  status      Show status"
    echo "  logs        Show logs"
    echo "  monitor     Monitor bot health"
    echo "  help        Show this help"
    echo ""
    echo "Examples:"
    echo "  sudo $0 deploy    # Full deployment"
    echo "  sudo $0 start     # Start bot"
    echo "  sudo $0 status    # Check status"
}

# Main function
main() {
    case "${1:-deploy}" in
        "deploy")
            deploy
            ;;
        "start")
            start_bot
            ;;
        "stop")
            pm2 stop "$BOT_NAME"
            ;;
        "restart")
            pm2 restart "$BOT_NAME"
            ;;
        "status")
            show_status
            ;;
        "logs")
            pm2 logs "$BOT_NAME" --lines 50
            ;;
        "monitor")
            /usr/local/bin/empire-webbot-monitor
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
