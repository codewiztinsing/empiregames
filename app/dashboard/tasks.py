import requests
from decouple import config
from celery import shared_task
from users.models import User



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


@shared_task
def send_message_to_all_players(message):
    users = User.objects.all()
    for user in users:
        send_message(user.telegram_id, message)
    return True