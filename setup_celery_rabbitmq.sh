#!/bin/bash

# Local Celery + RabbitMQ Setup Script for Liyu Bingo
# This script sets up RabbitMQ and Celery for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/tinsae/Desktop/projects/empiregames"
APP_DIR="$PROJECT_DIR/app"
VENV_DIR="$PROJECT_DIR/venv"
RABBITMQ_USER="liyu_user"
RABBITMQ_PASS="liyu_password"
RABBITMQ_VHOST="liyu_vhost"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Ubuntu/Debian
check_system() {
    if ! command -v apt-get &> /dev/null; then
        error "This script is designed for Ubuntu/Debian systems. Please adapt for your system."
        exit 1
    fi
}

# Install RabbitMQ
install_rabbitmq() {
    log "Installing RabbitMQ..."
    
    # Update package list
    sudo apt-get update
    
    # Install RabbitMQ
    sudo apt-get install -y rabbitmq-server
    
    # Enable and start RabbitMQ
    sudo systemctl enable rabbitmq-server
    sudo systemctl start rabbitmq-server
    
    # Enable management plugin
    sudo rabbitmq-plugins enable rabbitmq_management
    
    log "RabbitMQ installed and started successfully!"
}

# Configure RabbitMQ
configure_rabbitmq() {
    log "Configuring RabbitMQ..."
    
    # Create virtual host
    sudo rabbitmqctl add_vhost $RABBITMQ_VHOST
    
    # Create user
    sudo rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASS
    
    # Set permissions
    sudo rabbitmqctl set_permissions -p $RABBITMQ_VHOST $RABBITMQ_USER ".*" ".*" ".*"
    
    # Set user tags
    sudo rabbitmqctl set_user_tags $RABBITMQ_USER administrator
    
    log "RabbitMQ configured successfully!"
    info "RabbitMQ Management UI: http://localhost:15672"
    info "Username: $RABBITMQ_USER"
    info "Password: $RABBITMQ_PASS"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    cd $APP_DIR
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    log "Python dependencies installed successfully!"
}

# Run Django migrations
run_migrations() {
    log "Running Django migrations..."
    
    cd $APP_DIR
    source $VENV_DIR/bin/activate
    
    # Run migrations
    python manage.py migrate
    
    log "Django migrations completed successfully!"
}

# Create environment file
create_env_file() {
    log "Creating environment file..."
    
    cd $APP_DIR
    
    cat > .env << EOF
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Celery + RabbitMQ
CELERY_BROKER_URL=amqp://$RABBITMQ_USER:$RABBITMQ_PASS@localhost:5672/$RABBITMQ_VHOST
CELERY_RESULT_BACKEND=rpc://

# Bot Settings
BOT_TOKEN=your-bot-token-here
BACK_URL=http://localhost:8000
MANUAL_API_KEY=your-manual-api-key
MANUAL_BASE_URL=http://localhost:8000

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0
EOF
    
    log "Environment file created at $APP_DIR/.env"
    warn "Please update the .env file with your actual values!"
}

# Create Celery management scripts
create_celery_scripts() {
    log "Creating Celery management scripts..."
    
    cd $APP_DIR
    
    # Create start_celery_worker.sh
    cat > start_celery_worker.sh << 'EOF'
#!/bin/bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate
celery -A core worker -l info --concurrency=4
EOF
    
    # Create start_celery_beat.sh
    cat > start_celery_beat.sh << 'EOF'
#!/bin/bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
EOF
    
    # Create start_celery_flower.sh
    cat > start_celery_flower.sh << 'EOF'
#!/bin/bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate
celery -A core flower --port=5555
EOF
    
    # Create start_all_celery.sh
    cat > start_all_celery.sh << 'EOF'
#!/bin/bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate

# Start Celery Worker
echo "Starting Celery Worker..."
celery -A core worker -l info --concurrency=4 &
WORKER_PID=$!

# Start Celery Beat
echo "Starting Celery Beat..."
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
BEAT_PID=$!

# Start Celery Flower
echo "Starting Celery Flower..."
celery -A core flower --port=5555 &
FLOWER_PID=$!

echo "All Celery services started!"
echo "Worker PID: $WORKER_PID"
echo "Beat PID: $BEAT_PID"
echo "Flower PID: $FLOWER_PID"
echo ""
echo "Access Flower at: http://localhost:5555"
echo ""
echo "To stop all services, press Ctrl+C"

# Wait for interrupt
trap "kill $WORKER_PID $BEAT_PID $FLOWER_PID; exit" INT
wait
EOF
    
    # Make scripts executable
    chmod +x start_celery_worker.sh
    chmod +x start_celery_beat.sh
    chmod +x start_celery_flower.sh
    chmod +x start_all_celery.sh
    
    log "Celery management scripts created successfully!"
}

# Test Celery connection
test_celery() {
    log "Testing Celery connection..."
    
    cd $APP_DIR
    source $VENV_DIR/bin/activate
    
    # Test Celery worker
    python -c "
from celery import Celery
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
try:
    app.control.inspect().ping()
    print('✅ Celery connection successful!')
except Exception as e:
    print(f'❌ Celery connection failed: {e}')
"
    
    log "Celery connection test completed!"
}

# Show status
show_status() {
    log "Checking system status..."
    
    echo ""
    info "=== RabbitMQ Status ==="
    sudo systemctl status rabbitmq-server --no-pager -l
    
    echo ""
    info "=== RabbitMQ Management ==="
    echo "URL: http://localhost:15672"
    echo "Username: $RABBITMQ_USER"
    echo "Password: $RABBITMQ_PASS"
    
    echo ""
    info "=== Celery Scripts ==="
    echo "Worker: $APP_DIR/start_celery_worker.sh"
    echo "Beat: $APP_DIR/start_celery_beat.sh"
    echo "Flower: $APP_DIR/start_celery_flower.sh"
    echo "All: $APP_DIR/start_all_celery.sh"
    
    echo ""
    info "=== Environment File ==="
    echo "Location: $APP_DIR/.env"
    echo "Please update with your actual values!"
}

# Main function
main() {
    case "${1:-install}" in
        "install")
            check_system
            install_rabbitmq
            configure_rabbitmq
            install_dependencies
            run_migrations
            create_env_file
            create_celery_scripts
            test_celery
            show_status
            ;;
        "status")
            show_status
            ;;
        "test")
            test_celery
            ;;
        "restart-rabbitmq")
            sudo systemctl restart rabbitmq-server
            log "RabbitMQ restarted!"
            ;;
        "stop-rabbitmq")
            sudo systemctl stop rabbitmq-server
            log "RabbitMQ stopped!"
            ;;
        "start-rabbitmq")
            sudo systemctl start rabbitmq-server
            log "RabbitMQ started!"
            ;;
        *)
            echo "Usage: $0 {install|status|test|restart-rabbitmq|stop-rabbitmq|start-rabbitmq}"
            echo ""
            echo "Commands:"
            echo "  install           - Install and configure RabbitMQ + Celery"
            echo "  status            - Show system status"
            echo "  test              - Test Celery connection"
            echo "  restart-rabbitmq  - Restart RabbitMQ service"
            echo "  stop-rabbitmq     - Stop RabbitMQ service"
            echo "  start-rabbitmq    - Start RabbitMQ service"
            echo ""
            echo "After installation, you can start Celery services with:"
            echo "  ./start_all_celery.sh    # Start all services"
            echo "  ./start_celery_worker.sh # Start worker only"
            echo "  ./start_celery_beat.sh   # Start beat only"
            echo "  ./start_celery_flower.sh # Start flower only"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
