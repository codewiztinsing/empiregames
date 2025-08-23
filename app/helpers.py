from utils import get_bot_seetings

import requests
import logging
import string
import random

logger = logging.getLogger(__name__)


def generate_tx_ref(length=20):
    """Generate a transaction reference that contains only letters, numbers, hyphens, underscores, and dots."""
    characters = string.ascii_letters + string.digits + '-_.'
    tx_ref = ''.join(random.choice(characters) for _ in range(length))
    return tx_ref


def get_numbers_of_games_played(telegram_id: int) -> int:
    BACK_URL = get_bot_seetings().get("bot_url")
    logger.info(f"BACK_URL {BACK_URL}")
    response = requests.get(f"{BACK_URL}/api/v1/game/player-games-count/?telegram_id={telegram_id}")
    logger.info(f"response {response.json()}")
    return response.json().get("player_games_count", 0)


def helper_initialize_payment_chapa(amount,first_name,last_name,phone_number):
    BACK_URL = get_bot_seetings().get("bot_url")
    url = "/api/v1/wallet/chapa/create-session"
    full_url = f"{BACK_URL}{url}"
    
        
    data = {
            "amount": float(amount),
            "currency": "ETB",
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name}@gmail.com",
            "phone_number": phone_number,
            "tx_ref":generate_tx_ref(),
            "return_url":f"https://t.me/wowbingobotbotbot",
            "customization":{
                "title": "Wow Bingo",
                "description": "Deposit to Wow Bingo",
                "logo": "https://wowliyubingo.com/static/media/logo.png"
            },
            # "callback_url": "https://webhook.site/6bca0770-2235-4096-b8f6-41b861ec40e9"
            "callback_url": f"{BACK_URL}/api/v1/wallet/webhook/chapa/callback/"

    }
    logger.info(f"data = {data}")
    
    response = requests.post(full_url, json=data)
    if response.status_code == 200:
        chapa_session = initialize_payment(**data)
        logger.info(f"data = {chapa_session}")
        data = chapa_session.get("data")
        checkout_url = data.get("checkout_url")
        return checkout_url
    logger.info(f"response = {response.json()}")
    return response.json().get("data").get("checkout_url")



def daily_withdrawal_limit(telegram_id: int) -> int:
    BACK_URL = get_bot_seetings().get("bot_url")
    url = f"/api/v1/wallet/daily-withdrawal-limit/{telegram_id}"
    full_url = f"{BACK_URL}{url}"
    response = requests.get(full_url)
    return response.json().get("daily_withdrawal_limit")

     
