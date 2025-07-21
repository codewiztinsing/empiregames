import json
import logging
from ninja import Router
from users.models import User
from wallet.models import Wallet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Game, PlayerGame
from .tasks import charge_player,push_transaction,update_player_balance
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema
from ninja.errors import HttpError  # Correct import


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
game_router = Router()

@game_router.post("/join-game/",response=GameSchema)
def join_game(request, data: BetSchema):
    logger.info(f"Join game: {data}")
    game = get_object_or_404(Game,id=data.game_id)
    
    players = data.players
    players_dict = {}
    for player in players:
        players_dict[player.playerId] = player.numberOfBoards
    
    logger.info(f"Players dict: {players_dict}")
    
    charge_player.delay(players_dict,game.entry_fee,game.id)
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)    
    
   
    

@game_router.post("/win-game/",response=GameSchema)
def win_game(request, data: WinGameSchema):
    logger.info(f"Win game: {data}")
    game = get_object_or_404(Game,id=data.game_id)
    player = data.player
    win_amount = data.win_amount
    logger.info(f"Game: {game}")
    logger.info(f"Player: {player}")
    update_player_balance.delay(player,win_amount,game.id)
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)    

@game_router.get("/next-game/",response=GameSchema)
def next_game(request):
    logger.info(f"Next game: {request}")
    bet_amount = request.GET.get("bet_amount")
    game = Game.objects.filter(entry_fee=bet_amount,ended=False).first()
    logger.info(f"Game: {game}")
    if not game:
        game = Game.objects.create(entry_fee=bet_amount)
    logger.info(f"Game: {game}")
  
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)



@game_router.get("/update-last-game/",response=GameSchema)
def update_last_game(request):
    bet_amount = request.GET.get("bet_amount")
    game = Game.objects.filter(entry_fee=bet_amount).last()
    logger.info(f"Game: {game.id}")
   
    game.ended = True
    game.started = False
    game.save()
  
    return GameSchema(bet_amount=game.entry_fee,game_id=game.id)
   