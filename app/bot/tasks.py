import httpx
from celery import shared_task
from decouple import config


@shared_task(name='bot.tasks.send_photo_message')
def send_photo_message(chat_id: str, photo_url: str, caption: str = ""):
    """Send a photo message via Telegram Bot API.
    Routed to the 'notifications' queue (lower priority than payments).
    """
    token = config('BOT_TOKEN')
    if not token:
        return {"ok": False, "error": "BOT_TOKEN not configured"}

    api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        'chat_id': str(chat_id),
        'photo': photo_url,
        'caption': caption or "",
        'parse_mode': 'HTML'
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(api_url, data=payload)
            try:
                data = resp.json()
            except Exception:
                data = {"ok": False, "status_code": resp.status_code, "text": resp.text}
            return data
    except Exception as e:
        return {"ok": False, "error": str(e)}


