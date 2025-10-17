import requests
from decouple import config
from celery import shared_task
from users.models import User
import httpx
import logging
from django.conf import settings
import os
logger = logging.getLogger(__name__)




def send_text(telegram_id: str, text: str):
    bot_token = config('BOT_TOKEN')
    if not bot_token:
        return False
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': str(telegram_id), 'text': text, 'parse_mode': 'HTML'}
    try:
        with httpx.Client(timeout=15.0) as client:
            client.post(api_url, data=payload)
        return True
    except Exception:
        return False



def send_photo(telegram_id: str, photo_url: str, caption: str = ""):
    bot_token = config('BOT_TOKEN')
    if not bot_token:
        return False
    api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    # Resolve local media path to absolute file path if needed
    files = None
    data = {'chat_id': str(telegram_id), 'caption': caption or "", 'parse_mode': 'HTML'}
    # If photo_url looks like a local path (relative within MEDIA_ROOT), send as multipart
    try:
        if photo_url and not photo_url.startswith('http'):
            abs_path = os.path.join(settings.MEDIA_ROOT, photo_url) if not os.path.isabs(photo_url) else photo_url
            if os.path.exists(abs_path):
                files = {'photo': open(abs_path, 'rb')}
            else:
                # fallback to sending as URL if file missing
                data['photo'] = photo_url
        else:
            data['photo'] = photo_url
    except Exception:
        data['photo'] = photo_url
    try:
        with httpx.Client(timeout=20.0) as client:
            if files:
                client.post(api_url, data=data, files=files)
            else:
                client.post(api_url, data=data)
        return True
    except Exception:
        return False


@shared_task(queue='notifications')
def send_message_to_all_players(message: str, image_url: str | None = None, caption: str | None = None):
    """Broadcast a message to all users via Telegram.
    If image_url is provided, send photo with optional caption; otherwise send text.
    Routed to 'notifications' queue to avoid blocking payment tasks.
    """
    users = User.objects.all()
    logger.info(f"Sending message to all players: {message}")
    for user in users:
        chat_id = getattr(user, 'telegram_id', None)
        if not chat_id:
            continue
        if image_url:
            if not send_photo(chat_id, image_url, caption or message):
                send_text(chat_id, caption or message)
        else:
            send_text(chat_id, message)
    return True