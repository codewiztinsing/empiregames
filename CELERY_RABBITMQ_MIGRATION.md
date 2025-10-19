# Celery Migration Guide: Redis to RabbitMQ

## Overview
This guide covers migrating from Celery with Redis to Celery with RabbitMQ and setting up Celery Beat for local development.

## Migration Benefits

### RabbitMQ Advantages over Redis:
- **Better message durability** - Messages persist across broker restarts
- **Advanced routing** - Complex routing patterns and exchanges
- **Clustering support** - Built-in clustering and high availability
- **Management UI** - Rich web-based management interface
- **Protocol support** - Native AMQP protocol support
- **Dead letter queues** - Better error handling and retry mechanisms

## Migration Steps

### 1. Install RabbitMQ

#### Option A: Using the Setup Script (Recommended)
```bash
cd /home/tinsae/Desktop/projects/empiregames
chmod +x setup_celery_rabbitmq.sh
./setup_celery_rabbitmq.sh install
```

#### Option B: Manual Installation
```bash
# Install RabbitMQ
sudo apt-get update
sudo apt-get install -y rabbitmq-server

# Start and enable RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Create user and virtual host
sudo rabbitmqctl add_user liyu_user liyu_password
sudo rabbitmqctl add_vhost liyu_vhost
sudo rabbitmqctl set_permissions -p liyu_vhost liyu_user ".*" ".*" ".*"
sudo rabbitmqctl set_user_tags liyu_user administrator
```

### 2. Update Python Dependencies
```bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate
pip install -r requirements.txt
```

### 3. Update Configuration

#### Environment Variables
```bash
# Update your .env file
CELERY_BROKER_URL=amqp://liyu_user:liyu_password@localhost:5672/liyu_vhost
CELERY_RESULT_BACKEND=rpc://
```

#### Django Settings
The settings have been updated to use RabbitMQ by default:
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')
```

### 4. Run Migrations
```bash
cd /home/tinsae/Desktop/projects/empiregames/app
source /home/tinsae/Desktop/projects/empiregames/venv/bin/activate
python manage.py migrate
```

## Local Development Setup

### 1. Using Docker Compose (Recommended)
```bash
cd /home/tinsae/Desktop/projects/empiregames
docker-compose -f docker-compose.local.yml up -d
```

This will start:
- **RabbitMQ** (port 5672, management UI on 15672)
- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **Django** (port 8000)
- **Celery Worker**
- **Celery Beat**
- **Celery Flower** (port 5555)

### 2. Using Local Installation
```bash
# Start RabbitMQ
sudo systemctl start rabbitmq-server

# Start Celery services
cd /home/tinsae/Desktop/projects/empiregames/app
./start_all_celery.sh
```

## Service Management

### 1. Celery Management Scripts
The setup script creates several management scripts:

```bash
# Start all Celery services
./start_all_celery.sh

# Start individual services
./start_celery_worker.sh    # Celery Worker
./start_celery_beat.sh      # Celery Beat
./start_celery_flower.sh    # Celery Flower
```

### 2. Manual Service Management
```bash
# Start Celery Worker
celery -A core worker -l info --concurrency=4

# Start Celery Beat
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Start Celery Flower
celery -A core flower --port=5555
```

### 3. RabbitMQ Management
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Restart RabbitMQ
sudo systemctl restart rabbitmq-server

# Stop RabbitMQ
sudo systemctl stop rabbitmq-server

# Start RabbitMQ
sudo systemctl start rabbitmq-server
```

## Monitoring and Management

### 1. RabbitMQ Management UI
- **URL**: http://localhost:15672
- **Username**: liyu_user
- **Password**: liyu_password

Features:
- **Queue monitoring** - View message counts and rates
- **Connection management** - Monitor active connections
- **Exchange management** - Configure exchanges and bindings
- **User management** - Manage users and permissions
- **Performance metrics** - Monitor throughput and latency

### 2. Celery Flower
- **URL**: http://localhost:5555
- **Username**: admin
- **Password**: password

Features:
- **Task monitoring** - Real-time task execution
- **Worker status** - Monitor worker health and performance
- **Task history** - View completed and failed tasks
- **Performance metrics** - Track task execution times
- **Task retry management** - Manage failed task retries

### 3. Command Line Monitoring
```bash
# Check Celery worker status
celery -A core inspect active

# Check scheduled tasks
celery -A core inspect scheduled

# Check worker statistics
celery -A core inspect stats

# Purge all tasks
celery -A core purge

# Check RabbitMQ status
sudo rabbitmqctl status

# List queues
sudo rabbitmqctl list_queues

# List connections
sudo rabbitmqctl list_connections
```

## Configuration Examples

### 1. Basic Celery Configuration
```python
# app/celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-games': {
        'task': 'app.tasks.cleanup_old_games',
        'schedule': 3600.0,  # Every hour
    },
    'send-daily-stats': {
        'task': 'app.tasks.send_daily_stats',
        'schedule': 86400.0,  # Daily
    },
}

app.conf.timezone = 'UTC'
```

### 2. Advanced RabbitMQ Configuration
```python
# Advanced Celery configuration for RabbitMQ
CELERY_BROKER_URL = 'amqp://liyu_user:liyu_password@localhost:5672/liyu_vhost'
CELERY_RESULT_BACKEND = 'rpc://'

# RabbitMQ-specific settings
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# Message durability
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

# Task routing
CELERY_TASK_ROUTES = {
    'app.tasks.high_priority_task': {'queue': 'high_priority'},
    'app.tasks.low_priority_task': {'queue': 'low_priority'},
}
```

### 3. Queue Configuration
```python
# Define custom queues
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'high_priority': {
        'exchange': 'high_priority',
        'exchange_type': 'direct',
        'routing_key': 'high_priority',
    },
    'low_priority': {
        'exchange': 'low_priority',
        'exchange_type': 'direct',
        'routing_key': 'low_priority',
    },
}
```

## Task Examples

### 1. Basic Task
```python
# app/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_email, username):
    """Send welcome email to new user"""
    send_mail(
        'Welcome to Liyu Bingo!',
        f'Hello {username}, welcome to our bingo game!',
        'noreply@liyubingo.com',
        [user_email],
        fail_silently=False,
    )
    return f"Welcome email sent to {user_email}"
```

### 2. Periodic Task
```python
@shared_task
def cleanup_old_games():
    """Clean up games older than 24 hours"""
    from .models import Game
    from django.utils import timezone
    
    cutoff_time = timezone.now() - timezone.timedelta(hours=24)
    old_games = Game.objects.filter(created_at__lt=cutoff_time)
    count = old_games.count()
    old_games.delete()
    return f"Cleaned up {count} old games"
```

### 3. Task with Progress Updates
```python
@shared_task(bind=True)
def process_large_dataset(self, data):
    """Process large dataset with progress updates"""
    total = len(data)
    processed = 0
    
    for item in data:
        # Process item
        process_item(item)
        processed += 1
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': processed, 'total': total}
        )
    
    return {'current': processed, 'total': total, 'status': 'Task completed!'}
```

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Failed**
   ```bash
   # Check RabbitMQ status
   sudo systemctl status rabbitmq-server
   
   # Check RabbitMQ logs
   sudo journalctl -u rabbitmq-server -f
   
   # Test connection
   python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('localhost'))"
   ```

2. **Celery Worker Not Starting**
   ```bash
   # Check Celery logs
   celery -A core worker -l debug
   
   # Check Django settings
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.CELERY_BROKER_URL)
   ```

3. **Tasks Not Executing**
   ```bash
   # Check worker status
   celery -A core inspect active
   
   # Check queue status
   sudo rabbitmqctl list_queues
   
   # Check connections
   sudo rabbitmqctl list_connections
   ```

4. **Celery Beat Not Scheduling**
   ```bash
   # Check beat logs
   celery -A core beat -l debug
   
   # Check scheduled tasks
   celery -A core inspect scheduled
   
   # Check database scheduler
   python manage.py shell
   >>> from django_celery_beat.models import PeriodicTask
   >>> PeriodicTask.objects.all()
   ```

### Performance Optimization

1. **RabbitMQ Optimization**
   ```bash
   # Update RabbitMQ configuration
   sudo nano /etc/rabbitmq/rabbitmq.conf
   
   # Add performance settings
   vm_memory_high_watermark.relative = 0.6
   disk_free_limit.absolute = 1GB
   channel_max = 1000
   connection_max = 1000
   ```

2. **Celery Worker Optimization**
   ```python
   # Optimize worker settings
   CELERY_WORKER_CONCURRENCY = 4
   CELERY_WORKER_PREFETCH_MULTIPLIER = 1
   CELERY_TASK_ACKS_LATE = True
   CELERY_WORKER_DISABLE_RATE_LIMITS = True
   ```

## Migration Checklist

- [ ] Install RabbitMQ
- [ ] Configure RabbitMQ user and virtual host
- [ ] Update Python dependencies
- [ ] Update Django settings
- [ ] Update environment variables
- [ ] Run Django migrations
- [ ] Test Celery connection
- [ ] Start Celery services
- [ ] Verify task execution
- [ ] Test periodic tasks
- [ ] Configure monitoring
- [ ] Update deployment scripts

## Next Steps

1. **Test the migration** with sample tasks
2. **Monitor performance** using Flower and RabbitMQ management UI
3. **Configure production** settings for RabbitMQ
4. **Update Kubernetes** deployment to use RabbitMQ
5. **Set up monitoring** and alerting
6. **Document** any custom configurations

This migration provides a more robust and scalable message broker solution for your Celery-based task processing system.
