from celery import shared_task
from users.models import User
from wallet.models import Wallet
"""Chapa-related tasks removed."""
from wallet.models import Transaction
from decouple import config
import requests

@shared_task
def handle_deposit_success(tx_ref):
    # Removed provider-specific logic
    return False


def send_notification(telegram_id, title, message):
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