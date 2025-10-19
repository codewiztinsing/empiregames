# Celery tasks for Liyu Bingo
# app/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_email, username):
    """Send welcome email to new user"""
    try:
        send_mail(
            'Welcome to Liyu Bingo!',
            f'Hello {username}, welcome to our bingo game!',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user_email}")
        return f"Welcome email sent to {user_email}"
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {e}")
        raise

@shared_task
def cleanup_old_games():
    """Clean up games older than 24 hours"""
    try:
        from .models import Game
        cutoff_time = timezone.now() - timezone.timedelta(hours=24)
        old_games = Game.objects.filter(created_at__lt=cutoff_time)
        count = old_games.count()
        old_games.delete()
        logger.info(f"Cleaned up {count} old games")
        return f"Cleaned up {count} old games"
    except Exception as e:
        logger.error(f"Failed to cleanup old games: {e}")
        raise

@shared_task
def send_daily_stats():
    """Send daily statistics to administrators"""
    try:
        from .models import Game, User
        from django.utils import timezone
        
        today = timezone.now().date()
        games_today = Game.objects.filter(created_at__date=today).count()
        users_today = User.objects.filter(date_joined__date=today).count()
        
        message = f"""
        Daily Statistics for {today}:
        - Games played: {games_today}
        - New users: {users_today}
        """
        
        send_mail(
            f'Daily Stats - {today}',
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@liyubingo.com'],
            fail_silently=False,
        )
        
        logger.info(f"Daily stats sent for {today}")
        return f"Daily stats sent for {today}"
    except Exception as e:
        logger.error(f"Failed to send daily stats: {e}")
        raise

@shared_task
def backup_database():
    """Create database backup"""
    try:
        import subprocess
        import os
        from django.conf import settings
        
        # Create backup directory if it doesn't exist
        backup_dir = '/tmp/backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/backup_{timestamp}.sql"
        
        # Create backup
        subprocess.run([
            'pg_dump',
            settings.DATABASES['default']['NAME'],
            '-f', backup_file
        ], check=True)
        
        logger.info(f"Database backup created: {backup_file}")
        return f"Database backup created: {backup_file}"
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise

@shared_task(bind=True)
def process_large_dataset(self, data):
    """Process large dataset with progress updates"""
    try:
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
        
        logger.info(f"Processed {processed} items")
        return {'current': processed, 'total': total, 'status': 'Task completed!'}
    except Exception as e:
        logger.error(f"Failed to process dataset: {e}")
        raise

def process_item(item):
    """Helper function to process individual items"""
    # Add your item processing logic here
    pass

@shared_task
def send_notification(user_id, message):
    """Send notification to user"""
    try:
        from .models import User
        from django.core.mail import send_mail
        
        user = User.objects.get(id=user_id)
        
        send_mail(
            'Liyu Bingo Notification',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Notification sent to user {user_id}")
        return f"Notification sent to user {user_id}"
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        raise

@shared_task
def update_game_statistics():
    """Update game statistics"""
    try:
        from .models import Game, User
        
        # Calculate statistics
        total_games = Game.objects.count()
        total_users = User.objects.count()
        active_games = Game.objects.filter(status='in-progress').count()
        
        # Update statistics (you might want to store these in a separate model)
        stats = {
            'total_games': total_games,
            'total_users': total_users,
            'active_games': active_games,
            'updated_at': timezone.now()
        }
        
        logger.info(f"Game statistics updated: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Failed to update game statistics: {e}")
        raise

@shared_task
def send_reminder(user_id, game_id):
    """Send game reminder to user"""
    try:
        from .models import User, Game
        
        user = User.objects.get(id=user_id)
        game = Game.objects.get(id=game_id)
        
        message = f"""
        Hi {user.username},
        
        This is a reminder that your game #{game.id} is starting soon!
        
        Game details:
        - Game ID: {game.id}
        - Start time: {game.start_time}
        
        Good luck!
        """
        
        send_mail(
            f'Game Reminder - Game #{game.id}',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Reminder sent to user {user_id} for game {game_id}")
        return f"Reminder sent to user {user_id} for game {game_id}"
    except Exception as e:
        logger.error(f"Failed to send reminder to user {user_id} for game {game_id}: {e}")
        raise
