import logging
from celery import shared_task
from game.models import PlayerGame

logger = logging.getLogger(__name__)

@shared_task
def charge_player(player_game_id, entry_fee, game_id):
    logger.info(f"Charge player: {player_game_id}, {entry_fee}, {game_id}")
    player_game = PlayerGame.objects.get(id=player_game_id)
    logger.info(f"Player game: {player_game}")
    player_game.user.wallet.balance -= float(entry_fee)
    player_game.user.wallet.save()
    return player_game.user.wallet.balance


