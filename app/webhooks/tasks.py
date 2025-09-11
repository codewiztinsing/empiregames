from celery import shared_task
from users.models import User
from wallet.models import Wallet
from wallet.models import ChapaSession
from wallet.models import Transaction
from decouple import config
import requests

@shared_task
def handle_deposit_success(tx_ref):
    chapa_session = ChapaSession.objects.filter(tx_ref=tx_ref).first()
    if chapa_session:
        chapa_session.status = "success"
        chapa_session.save()
        user = User.objects.filter(phone=chapa_session.phone_number).first()
        if user:
            wallet = Wallet.objects.filter(user=user).first()
            if wallet:
                wallet.balance += float(chapa_session.amount)
                wallet.save()
                transaction = Transaction.objects.create(user=user,amount=chapa_session.amount,type="DEPOSIT",status="success",reference=chapa_session.tx_ref)
                # push notification to user
                send_notification(user.telegram_id, "Deposit successful", "Your deposit of {chapa_session.amount} ETB has been successful")
                return True
            else:
                return False
        else:
            return False
    else:
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