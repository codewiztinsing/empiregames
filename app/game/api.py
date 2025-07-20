import json
import logging
from ninja import Router
from users.models import User
from wallet.models import Wallet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Game, PlayerGame
from .tasks import charge_player
from .schema import BetSchema,GameSchema,NextGameSchema
from ninja.errors import HttpError  # Correct import


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
game_router = Router()

@game_router.post("/join-game/",response=GameSchema)
def join_game(request, data: BetSchema):
    logger.info(f"Join game: {data}")
    game = get_object_or_404(Game,id=data.game_id)
    logger.info(f"Game: {game}")
    for player in data.players:
        player = get_object_or_404(User,telegram_id=player)
        logger.info(f"Player {player.id}")
        logger.info(f"Player: {player}")
        logger.info(f"Player balance: {player.wallet.balance}")
        logger.info(f"Game entry fee: {game.entry_fee}")
        try:
            player_game = PlayerGame.objects.create(user=player, game=game)
            charge_player.delay(player_game.id,game.entry_fee,game.id)
            logger.info(f"Player game created: {player_game}")
        except Exception as e:
            logger.error(f"Player already joined the game: {e}")
            raise HttpError(400, "Player already joined the game")
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)    
    
   
    


@game_router.get("/next-game/",response=GameSchema)
def next_game(request,data:NextGameSchema):
    logger.info(f"Next game: {data}")

    game = Game.objects.filter(entry_fee=data.bet_amount,started=False).last()
    logger.info(f"Game: {game}")
    if not game:
        Game.objects.create(entry_fee=data.bet_amount)
        game = Game.objects.filter(entry_fee=data.bet_amount).last()
    logger.info(f"Game: {game}")
  
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)
   