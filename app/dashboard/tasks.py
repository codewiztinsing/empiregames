import requests
from decouple import config
from celery import shared_task
from users.models import User
from django.utils import timezone
import time


def send_message(telegram_id, message):
    bot_token = config('BOT_TOKEN')
    if bot_token:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        telegram_payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(telegram_url, json=telegram_payload, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    else:
        return False


@shared_task
def send_message_to_all_players(message):
    users = User.objects.all()
    for user in users:
        send_message(user.telegram_id, message)
    return True


@shared_task
def broadcast_message_with_progress(broadcast_id):
    """
    Send message to all users with progress tracking
    """
    from .models import BroadcastMessage
    
    try:
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        broadcast.status = 'sending'
        broadcast.save()
        
        # Get all users with telegram_id
        users = User.objects.filter(telegram_id__isnull=False).exclude(telegram_id='')
        broadcast.total_recipients = users.count()
        broadcast.save()
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                success = send_message(user.telegram_id, broadcast.message)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                
                # Update progress
                broadcast.sent_count = sent_count
                broadcast.failed_count = failed_count
                broadcast.save()
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                broadcast.failed_count = failed_count
                broadcast.save()
                continue
        
        # Mark as completed
        broadcast.status = 'completed'
        broadcast.completed_at = timezone.now()
        broadcast.save()
        
        return True
        
    except BroadcastMessage.DoesNotExist:
        return False
    except Exception as e:
        broadcast.status = 'failed'
        broadcast.error_message = str(e)
        broadcast.save()
        return False