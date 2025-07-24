from utils import initialize_payment,get_bot_seetings   
import requests
import logging

logger = logging.getLogger(__name__)


def get_numbers_of_games_played(telegram_id: int) -> int:
    BACK_URL = get_bot_seetings().get("bot_url")
    logger.info(f"BACK_URL {BACK_URL}")
    response = requests.get(f"{BACK_URL}/api/v1/game/player-games-count/?telegram_id={telegram_id}")
    logger.info(f"response {response.json()}")
    return response.json().get("player_games_count", 0)

