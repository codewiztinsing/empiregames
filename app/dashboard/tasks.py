import requests
from decouple import config
from celery import shared_task
from users.models import User
import os



def send_message(telegram_id, message):
    bot_token = config('BOT_TOKEN')
    if bot_token:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        telegram_payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(telegram_url, json=telegram_payload)
    else:
        return False


def send_photo(telegram_id, photo_url_or_path, caption=None):
    bot_token = config('BOT_TOKEN')
    if not bot_token:
        print("No bot token found")
        return False
    
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    data = {
        'chat_id': telegram_id,
        'caption': caption or '',
        'parse_mode': 'HTML'
    }
    files = None
    
    try:
        if photo_url_or_path and photo_url_or_path.startswith('http'):
            # Handle URL
            data['photo'] = photo_url_or_path
            response = requests.post(telegram_url, data=data, timeout=10)
            print(f"URL photo sent to {telegram_id}, status: {response.status_code}")
            return response.status_code == 200
            
        elif photo_url_or_path:
            # Handle file path - construct full path for Django media files
            from django.conf import settings
            full_path = os.path.join(settings.MEDIA_ROOT, photo_url_or_path)
            
            if os.path.exists(full_path):
                files = {'photo': open(full_path, 'rb')}
                response = requests.post(telegram_url, data=data, files=files, timeout=30)
                print(f"File photo sent to {telegram_id}, status: {response.status_code}")
                return response.status_code == 200
            else:
                print(f"File not found: {full_path}")
                return False
        else:
            print("No photo URL or path provided")
            return False
            
    except Exception as e:
        print(f"Error sending photo to {telegram_id}: {e}")
        return False
    finally:
        if files and hasattr(files.get('photo'), 'close'):
            files['photo'].close()


@shared_task
def send_message_to_all_players(message, image=None, caption=None):
    print(f"Starting broadcast: message='{message}', image='{image}', caption='{caption}'")
    users = User.objects.all().only('telegram_id')
    print(f"Found {users.count()} users to broadcast to")
    
    for user in users:
        try:
            if image:
                print(f"Sending photo to user {user.telegram_id}")
                # Use caption if provided, otherwise use message as caption
                photo_caption = caption if caption else message
                ok = send_photo(user.telegram_id, image, photo_caption)
                if not ok:
                    print(f"Photo failed for user {user.telegram_id}, sending text fallback")
                    send_message(user.telegram_id, message)
            else:
                print(f"Sending text message to user {user.telegram_id}")
                send_message(user.telegram_id, message)
        except Exception as e:
            print(f"Error sending to user {user.telegram_id}: {e}")
            continue
    
    print("Broadcast completed")
    return True