# Celery Configuration and Documentation

## Overview
This document covers the Celery configuration for the Liyu Bingo application deployed on Kubernetes. Celery is used for asynchronous task processing, scheduled tasks, and background job management.

## Architecture

### Components
1. **Celery Worker** - Processes background tasks
2. **Celery Beat** - Schedules periodic tasks
3. **Celery Flower** - Web-based monitoring dashboard
4. **Redis** - Message broker and result backend

### Architecture Diagram
```
Django App → Redis → Celery Worker
     ↓           ↓
Celery Beat → Redis → Celery Flower (Monitoring)
```

## Kubernetes Deployment

### 1. Celery Worker Deployment
- **Replicas**: 3 (scalable to 10)
- **Resources**: 256Mi-512Mi memory, 100m-200m CPU
- **Health Checks**: Liveness and readiness probes
- **Auto-scaling**: HPA based on CPU/Memory usage

### 2. Celery Beat Deployment
- **Replicas**: 1 (singleton for scheduling)
- **Resources**: 128Mi-256Mi memory, 50m-100m CPU
- **Purpose**: Periodic task scheduling

### 3. Celery Flower Deployment
- **Replicas**: 1 (monitoring dashboard)
- **Resources**: 128Mi-256Mi memory, 50m-100m CPU
- **Access**: Available at `/flower/` endpoint
- **Authentication**: Basic auth (admin:password)

## Configuration

### Environment Variables
```yaml
# Celery Configuration
CELERY_BROKER_URL: "redis://redis-service:6379/0"
CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
DJANGO_SETTINGS_MODULE: "core.settings_production"

# Database Configuration
DATABASE_URL: "postgresql://user:password@postgres-service:5432/dbname"

# Django Configuration
DJANGO_SECRET_KEY: "your-secret-key"
DEBUG: "False"
ALLOWED_HOSTS: "your-domain.com"
```

### Django Settings (settings_production.py)
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Celery Beat Configuration
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Worker Configuration
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = True

# Celery Monitoring
CELERY_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
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
# app/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Game

@shared_task
def cleanup_old_games():
    """Clean up games older than 24 hours"""
    cutoff_time = timezone.now() - timezone.timedelta(hours=24)
    old_games = Game.objects.filter(created_at__lt=cutoff_time)
    count = old_games.count()
    old_games.delete()
    return f"Cleaned up {count} old games"
```

### 3. Complex Task with Progress
```python
# app/tasks.py
from celery import shared_task
from celery import current_task

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

## Scheduled Tasks

### 1. Database Scheduler
```python
# app/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('core')

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-games': {
        'task': 'app.tasks.cleanup_old_games',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'send-daily-stats': {
        'task': 'app.tasks.send_daily_stats',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'backup-database': {
        'task': 'app.tasks.backup_database',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),  # Weekly on Monday
    },
}
```

### 2. Dynamic Scheduling
```python
# app/tasks.py
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

def schedule_reminder_task(user_id, reminder_time):
    """Schedule a one-time reminder task"""
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=reminder_time.hour,
        minute=reminder_time.minute,
        day_of_month=reminder_time.day,
        month_of_year=reminder_time.month,
    )
    
    task = PeriodicTask.objects.create(
        crontab=schedule,
        name=f'reminder-{user_id}-{reminder_time}',
        task='app.tasks.send_reminder',
        args=json.dumps([user_id]),
        one_off=True,  # Run only once
    )
    
    return task
```

## Monitoring and Management

### 1. Flower Dashboard
- **URL**: `https://your-domain.com/flower/`
- **Authentication**: admin:password
- **Features**:
  - Real-time task monitoring
  - Worker status
  - Task history
  - Performance metrics
  - Task retry management

### 2. Command Line Monitoring
```bash
# Check worker status
kubectl exec -it deployment/celery-worker -n liyu-bingo -- celery -A core inspect active

# Check scheduled tasks
kubectl exec -it deployment/celery-beat -n liyu-bingo -- celery -A core inspect scheduled

# Check task statistics
kubectl exec -it deployment/celery-worker -n liyu-bingo -- celery -A core inspect stats

# Purge all tasks
kubectl exec -it deployment/celery-worker -n liyu-bingo -- celery -A core purge
```

### 3. Django Admin Integration
```python
# app/admin.py
from django.contrib import admin
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

admin.site.register(PeriodicTask)
admin.site.register(CrontabSchedule)
admin.site.register(IntervalSchedule)
```

## Deployment Commands

### 1. Deploy Celery
```bash
# Deploy all Celery components
kubectl apply -f k8s/10-celery.yaml

# Check deployment status
kubectl get pods -l app=celery-worker -n liyu-bingo
kubectl get pods -l app=celery-beat -n liyu-bingo
kubectl get pods -l app=celery-flower -n liyu-bingo
```

### 2. Scale Celery Workers
```bash
# Scale workers
kubectl scale deployment celery-worker --replicas=5 -n liyu-bingo

# Using deployment script
./k8s-deploy.sh scale 3 2 3 3 5  # django bot nodejs react celery
```

### 3. Check Logs
```bash
# Worker logs
./k8s-deploy.sh logs celery

# Beat logs
./k8s-deploy.sh logs celery-beat

# Flower logs
./k8s-deploy.sh logs celery-flower

# All logs
./k8s-deploy.sh logs all
```

## Performance Optimization

### 1. Worker Configuration
```python
# Optimize worker performance
CELERY_WORKER_CONCURRENCY = 4  # Number of worker processes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Prefetch tasks
CELERY_TASK_ACKS_LATE = True  # Acknowledge tasks after completion
CELERY_WORKER_DISABLE_RATE_LIMITS = True  # Disable rate limiting
```

### 2. Task Optimization
```python
# Task routing and prioritization
CELERY_TASK_ROUTES = {
    'app.tasks.high_priority_task': {'queue': 'high_priority'},
    'app.tasks.low_priority_task': {'queue': 'low_priority'},
}

# Task time limits
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes
```

### 3. Redis Optimization
```yaml
# Redis configuration for Celery
redis:
  maxmemory: "512mb"
  maxmemory-policy: "allkeys-lru"
  save: "900 1 300 10 60 10000"
```

## Error Handling and Retry Logic

### 1. Task Retry Configuration
```python
# app/tasks.py
from celery import shared_task
from celery.exceptions import Retry

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def unreliable_task(self, data):
    """Task with retry logic"""
    try:
        # Process data
        result = process_data(data)
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 2. Error Notifications
```python
# app/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_error_notification(error_message, task_name):
    """Send error notification to administrators"""
    send_mail(
        f'Celery Task Error: {task_name}',
        f'Error: {error_message}',
        'noreply@liyubingo.com',
        ['admin@liyubingo.com'],
        fail_silently=False,
    )
```

## Security Considerations

### 1. Flower Authentication
```python
# Update Flower authentication in production
FLOWER_BASIC_AUTH = "admin:secure-password"
```

### 2. Task Security
```python
# Secure task execution
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_ALWAYS_EAGER = False  # Never execute tasks synchronously
```

### 3. Network Security
```yaml
# Network policies for Celery
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: celery-network-policy
  namespace: liyu-bingo
spec:
  podSelector:
    matchLabels:
      app: celery-worker
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: django-backend
    ports:
    - protocol: TCP
      port: 6379
```

## Troubleshooting

### Common Issues

1. **Workers Not Starting**
   ```bash
   kubectl describe pod -l app=celery-worker -n liyu-bingo
   kubectl logs -l app=celery-worker -n liyu-bingo
   ```

2. **Tasks Not Executing**
   ```bash
   # Check Redis connection
   kubectl exec -it deployment/redis -n liyu-bingo -- redis-cli ping
   
   # Check worker status
   kubectl exec -it deployment/celery-worker -n liyu-bingo -- celery -A core inspect active
   ```

3. **Beat Scheduler Issues**
   ```bash
   # Check beat logs
   kubectl logs -l app=celery-beat -n liyu-bingo
   
   # Check scheduled tasks
   kubectl exec -it deployment/celery-beat -n liyu-bingo -- celery -A core inspect scheduled
   ```

4. **Flower Not Accessible**
   ```bash
   # Check service
   kubectl get svc celery-flower-service -n liyu-bingo
   
   # Check ingress
   kubectl describe ingress liyu-bingo-ingress -n liyu-bingo
   ```

### Performance Issues

1. **High Memory Usage**
   ```bash
   # Check resource usage
   kubectl top pods -l app=celery-worker -n liyu-bingo
   
   # Scale workers
   kubectl scale deployment celery-worker --replicas=5 -n liyu-bingo
   ```

2. **Slow Task Processing**
   ```bash
   # Check task queue
   kubectl exec -it deployment/celery-worker -n liyu-bingo -- celery -A core inspect active
   
   # Check Redis memory
   kubectl exec -it deployment/redis -n liyu-bingo -- redis-cli info memory
   ```

## Best Practices

### 1. Task Design
- Keep tasks idempotent
- Use appropriate timeouts
- Handle exceptions gracefully
- Use task routing for different priorities

### 2. Monitoring
- Monitor task success rates
- Set up alerts for failed tasks
- Track performance metrics
- Regular health checks

### 3. Scaling
- Scale workers based on queue length
- Use different queues for different task types
- Monitor resource usage
- Implement circuit breakers

### 4. Maintenance
- Regular cleanup of old results
- Monitor Redis memory usage
- Update task configurations
- Test failover scenarios

## Integration with Django

### 1. Task Calling
```python
# In Django views
from .tasks import send_welcome_email

def register_user(request):
    # ... user registration logic ...
    
    # Send welcome email asynchronously
    send_welcome_email.delay(user.email, user.username)
    
    return HttpResponse("User registered successfully!")
```

### 2. Task Results
```python
# Check task results
from .tasks import process_large_dataset

def process_data(request):
    # Start task
    task = process_large_dataset.delay(data)
    
    # Check status
    if task.ready():
        result = task.result
    else:
        result = "Task is still processing..."
    
    return JsonResponse({'status': result})
```

### 3. Periodic Tasks
```python
# Create periodic tasks programmatically
from django_celery_beat.models import PeriodicTask, CrontabSchedule

def create_daily_report_task():
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=9,
        minute=0,
    )
    
    task = PeriodicTask.objects.create(
        crontab=schedule,
        name='daily-report',
        task='app.tasks.generate_daily_report',
        enabled=True,
    )
    
    return task
```

This comprehensive Celery configuration provides a robust foundation for asynchronous task processing in your Kubernetes-deployed Liyu Bingo application.
