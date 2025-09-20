import requests
from decouple import config
from celery import shared_task
from users.models import User
# Construct full URL for the image
from django.conf import settings
from django.utils import timezone
import time


def send_message(telegram_id, message, image_url=None):
    print(f"Sending message to {telegram_id}: {message}")
    print(f"Image URL: {image_url}")
    bot_token = config('BOT_TOKEN')
    if not bot_token:
        print("No BOT_TOKEN configured")
        return False
    
    try:
        print(f"Sending photo to {telegram_id}: {image_url}")
        if image_url:
            print(f"Sending photo to {telegram_id}: {image_url}")
            # Send photo with caption
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            telegram_payload = {
                'chat_id': telegram_id,
                'photo': image_url,
                'caption': message,
                'parse_mode': 'HTML'
            }
            print(f"Sending photo to {telegram_id}: {image_url}")
        else:
            # Send text message
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            telegram_payload = {
                'chat_id': telegram_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            print(f"Sending text to {telegram_id}")
        
        response = requests.post(telegram_url, json=telegram_payload, timeout=10)
        print(f"Telegram API response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram API error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
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
                # Get image URL if available
                image_url = None
                if broadcast.image:
                    # Use the proper way to get the full URL
                    image_url = f"{config('BASE_URL')}{broadcast.image.url}"
                    print(f"Sending image URL: {image_url}")  # Debug log
                
                success = send_message(user.telegram_id, broadcast.message, image_url)
                print(f"Success: {success}")
                if success:
                    sent_count += 1
                    print(f"Message sent successfully to user {user.telegram_id}")  # Debug log
                else:
                    failed_count += 1
                    print(f"Failed to send message to user {user.telegram_id}")  # Debug log
                
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
                print(f"Exception sending to user {user.telegram_id}: {str(e)}")  # Debug log
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