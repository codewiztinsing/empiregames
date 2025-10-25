#!/bin/bash

# Empire Games Support Bot - PM2 Management Script
# Professional deployment and management script

set -e  # Exit on any error

# Configuration
BOT_NAME="empire-support-bot"
BOT_DIR="/home/tinsae/Desktop/projects/empiregames/app/bot"
PYTHON_ENV="/home/tinsae/Desktop/projects/empiregames/app/venv"
LOG_DIR="/home/tinsae/Desktop/projects/empiregames/logs"
CONFIG_FILE="config.env"

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
        exit 1
    fi
    log "Virtual environment found at $PYTHON_ENV"
}

# Check if config file exists
check_config() {
    if [ ! -f "$BOT_DIR/$CONFIG_FILE" ]; then
        warning "Config file $CONFIG_FILE not found. Creating from example..."
        if [ -f "$BOT_DIR/config.env.example" ]; then
            cp "$BOT_DIR/config.env.example" "$BOT_DIR/$CONFIG_FILE"
            warning "Please edit $BOT_DIR/$CONFIG_FILE with your bot token"
            exit 1
        else
            error "No config file found. Please create $BOT_DIR/$CONFIG_FILE"
            exit 1
        fi
    fi
    log "Config file found"
}

# Create log directory
create_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        log "Created log directory: $LOG_DIR"
    fi
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    source "$PYTHON_ENV/bin/activate"
    pip install -r "$BOT_DIR/../requirements.txt" --quiet
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
    pm2 start support.py \
        --name "$BOT_NAME" \
        --interpreter "$PYTHON_ENV/bin/python" \
        --log "$LOG_DIR/support-bot.log" \
        --error "$LOG_DIR/support-bot-error.log" \
        --out "$LOG_DIR/support-bot-out.log" \
        --merge-logs \
        --log-date-format "YYYY-MM-DD HH:mm:ss" \
        --restart-delay 5000 \
        --max-restarts 10 \
        --min-uptime "10s" \
        --env-file "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        success "Bot started successfully!"
        log "Bot logs: $LOG_DIR/support-bot.log"
        log "Error logs: $LOG_DIR/support-bot-error.log"
    else
        error "Failed to start bot"
        exit 1
    fi
}

# Stop the bot
stop_bot() {
    log "Stopping $BOT_NAME..."
    pm2 stop "$BOT_NAME"
    success "Bot stopped"
}

# Restart the bot
restart_bot() {
    log "Restarting $BOT_NAME..."
    pm2 restart "$BOT_NAME"
    success "Bot restarted"
}

# Show bot status
status_bot() {
    log "Bot status:"
    pm2 status "$BOT_NAME"
}

# Show bot logs
logs_bot() {
    log "Showing bot logs (press Ctrl+C to exit):"
    pm2 logs "$BOT_NAME" --lines 50
}

# Show real-time logs
tail_logs() {
    log "Showing real-time logs (press Ctrl+C to exit):"
    pm2 logs "$BOT_NAME" --follow
}

# Monitor bot
monitor_bot() {
    log "Opening PM2 monitoring dashboard..."
    pm2 monit
}

# Save PM2 configuration
save_pm2() {
    log "Saving PM2 configuration..."
    pm2 save
    success "PM2 configuration saved"
}

# Setup PM2 startup script
setup_startup() {
    log "Setting up PM2 startup script..."
    pm2 startup
    success "PM2 startup script configured"
    warning "Run 'pm2 save' to save current processes"
}

# Clean logs
clean_logs() {
    log "Cleaning old logs..."
    pm2 flush "$BOT_NAME"
    success "Logs cleaned"
}

# Show help
show_help() {
    echo "Empire Games Support Bot - PM2 Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the bot with PM2"
    echo "  stop        Stop the bot"
    echo "  restart     Restart the bot"
    echo "  status      Show bot status"
    echo "  logs        Show bot logs"
    echo "  tail        Show real-time logs"
    echo "  monitor     Open PM2 monitoring dashboard"
    echo "  save        Save PM2 configuration"
    echo "  setup       Setup PM2 startup script"
    echo "  clean       Clean old logs"
    echo "  install     Install dependencies"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the bot"
    echo "  $0 logs     # View logs"
    echo "  $0 monitor  # Open monitoring dashboard"
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            check_pm2
            check_venv
            check_config
            create_log_dir
            install_dependencies
            start_bot
            ;;
        "stop")
            stop_bot
            ;;
        "restart")
            restart_bot
            ;;
        "status")
            status_bot
            ;;
        "logs")
            logs_bot
            ;;
        "tail")
            tail_logs
            ;;
        "monitor")
            monitor_bot
            ;;
        "save")
            save_pm2
            ;;
        "setup")
            setup_startup
            ;;
        "clean")
            clean_logs
            ;;
        "install")
            check_venv
            install_dependencies
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
