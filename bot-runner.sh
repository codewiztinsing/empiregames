#!/bin/bash

# Liyu Bingo Telegram Bot Production Runner
# This script sets up and runs the Telegram bot in production

set -e

# Configuration
PROJECT_DIR="/home/tinsae/Desktop/projects/empiregames/app"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/liyu-bot"
PID_FILE="/var/run/liyu-bot.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        error "Virtual environment not found at $VENV_DIR"
        error "Please create a virtual environment first:"
        error "cd $PROJECT_DIR && python3 -m venv venv"
        exit 1
    fi
}

# Check if Django project exists
check_django() {
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        error "Django project not found at $PROJECT_DIR"
        exit 1
    fi
}

# Create log directory
create_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        log "Creating log directory: $LOG_DIR"
        sudo mkdir -p "$LOG_DIR"
        sudo chown $USER:$USER "$LOG_DIR"
    fi
}

# Install dependencies
install_deps() {
    log "Installing Python dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install -r "$PROJECT_DIR/requirements.txt"
    
    # Install additional bot dependencies if not in requirements.txt
    pip install python-telegram-bot python-decouple requests
}

# Run Django migrations
run_migrations() {
    log "Running Django migrations..."
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    python manage.py migrate --noinput
}

# Collect static files
collect_static() {
    log "Collecting static files..."
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    python manage.py collectstatic --noinput
}

# Start the bot
start_bot() {
    log "Starting Liyu Bingo Telegram Bot..."
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    
    # Run the bot with proper logging
    python manage.py run_bot 2>&1 | tee -a "$LOG_DIR/bot.log" &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    log "Bot started with PID: $(cat $PID_FILE)"
    log "Logs are being written to: $LOG_DIR/bot.log"
}

# Stop the bot
stop_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log "Stopping bot (PID: $PID)..."
            kill $PID
            rm -f "$PID_FILE"
            log "Bot stopped"
        else
            warning "Bot process not found"
            rm -f "$PID_FILE"
        fi
    else
        warning "PID file not found. Bot may not be running."
    fi
}

# Restart the bot
restart_bot() {
    log "Restarting bot..."
    stop_bot
    sleep 2
    start_bot
}

# Check bot status
status_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log "Bot is running (PID: $PID)"
            return 0
        else
            warning "Bot is not running (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        warning "Bot is not running"
        return 1
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_DIR/bot.log" ]; then
        tail -f "$LOG_DIR/bot.log"
    else
        error "Log file not found: $LOG_DIR/bot.log"
    fi
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            check_root
            check_venv
            check_django
            create_log_dir
            install_deps
            run_migrations
            collect_static
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
            show_logs
            ;;
        "install")
            check_root
            check_venv
            check_django
            create_log_dir
            install_deps
            run_migrations
            collect_static
            log "Installation complete. Run './bot-runner.sh start' to start the bot."
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|install}"
            echo ""
            echo "Commands:"
            echo "  start   - Start the bot"
            echo "  stop    - Stop the bot"
            echo "  restart - Restart the bot"
            echo "  status  - Check bot status"
            echo "  logs    - Show live logs"
            echo "  install - Install dependencies and setup"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
