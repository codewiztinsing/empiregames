import json
import logging
from ninja import Router
from users.models import User
from wallet.models import Wallet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Game, PlayerGame,GameSettings,GameType
from .tasks import charge_player,push_transaction,update_player_balance,update_game_status,create_player_games,end_game
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema,GameSettingsSchema,GameTypeSchema,GameDetailsSchema,PlayerGameSchema
from ninja.errors import HttpError  # Correct import


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
game_router = Router()

@game_router.post("/join-game/", response=GameSchema)
def join_game(request, data: BetSchema):
    logger.info(f"Join game request: {data}")
    
    try:
        # Get the game
        game = get_object_or_404(Game, id=data.game_id)
        logger.info(f"Found game: {game.id} with entry fee: {game.entry_fee}")
        
        # Convert players to dictionary format
        players_dict = {}
        for player in data.players:
            players_dict[player.playerId] = player.numberOfBoards
        logger.info(f"Players dict: {players_dict}")
        
        # Create PlayerGame entities asynchronously
        create_player_games.delay(game.id, players_dict)
        
        # Charge players asynchronously
        charge_player.delay(players_dict, game.entry_fee, game.id)
        
        logger.info(f"Successfully processed join-game for game {game.id}")
        return GameSchema(bet_amount=game.entry_fee, game_id=game.id, playerId=0)
        
    except Exception as e:
        logger.error(f"Error in join_game: {e}")
        raise HttpError(500, f"Failed to join game: {str(e)}")    
    
   
    

@game_router.post("/win-game/", response=GameSchema)
def win_game(request, data: WinGameSchema):
    logger.info(f"Win game request: {data}")
    
    try:
        # Get the game
        game = get_object_or_404(Game, id=data.game_id)
        logger.info(f"Found game: {game.id}")
        
        # Validate player exists
        player_telegram_id = data.playerId
        player = get_object_or_404(User, telegram_id=player_telegram_id)
        logger.info(f"Found player: {player.username} (telegram_id: {player_telegram_id})")
        
        win_amount = data.win_amount
        logger.info(f"Win amount: {win_amount}")
        
        # Update player balance and game status asynchronously
        # This will also set the game winner and mark PlayerGame as bingo
        update_player_balance.delay(player_telegram_id, win_amount, game.id)
        
        logger.info(f"Successfully processed win-game for game {game.id}, winner: {player.username}")
        return GameSchema(bet_amount=game.entry_fee, game_id=game.id, playerId=player_telegram_id)
        
    except Exception as e:
        logger.error(f"Error in win_game: {e}")
        raise HttpError(500, f"Failed to process win: {str(e)}")    

@game_router.get("/next-game/",response=GameSchema)
def next_game(request):
    logger.info(f"Next game: {request}")
    bet_amount = request.GET.get("bet_amount")
    game = Game.objects.filter(entry_fee=bet_amount,ended=False).first()
    logger.info(f"Game: {game}")
    if not game:
        game = Game.objects.create(entry_fee=bet_amount)
    logger.info(f"Game: {game}")
  
    return GameSchema(bet_amount=game.entry_fee, game_id=game.id, playerId=0)



@game_router.get("/update-last-game/",response=GameSchema)
def update_last_game(request):
    bet_amount = request.GET.get("bet_amount")
    game = Game.objects.filter(entry_fee=bet_amount).last()
    winner = request.GET.get("winner")
    
    logger.info(f"Game: {game.id}")
    game.ended = True
    game.started = False
    game.save()
  
    return GameSchema(bet_amount=game.entry_fee, game_id=game.id, playerId=0)


@game_router.get("/game-settings/",response=GameSettingsSchema)
def game_settings(request):
    logger.info(f"Game settings: {request}")
    game_settings = GameSettings.objects.first()
    if not game_settings:
        game_settings = GameSettings.objects.create(game_speed=5000,count_down_time=30)
    return GameSettingsSchema(game_speed=game_settings.game_speed,count_down_time=game_settings.count_down_time)


@game_router.get("/game-types/", response=GameTypeSchema)
def game_types(request):
    logger.info(f"Game types: {request}")
    game_types = GameType.objects.all().order_by('-id')
    return GameTypeSchema(game_types=game_types)

@game_router.get("/game-details/<int:game_id>/", response=GameDetailsSchema)
def get_game_details(request, game_id: int):
    logger.info(f"Get game details for game_id: {game_id}")
    
    try:
        game = get_object_or_404(Game, id=game_id)
        logger.info(f"Found game: {game.id}")
        
        # Get all players in this game
        player_games = PlayerGame.objects.filter(game=game)
        players_data = []
        
        for player_game in player_games:
            players_data.append(PlayerGameSchema(
                id=player_game.user.id,
                username=player_game.user.username,
                has_bingo=player_game.has_bingo
            ))
        
        # Get winner name if exists
        winner_name = None
        if game.winner:
            winner_name = game.winner.username
        
        return GameDetailsSchema(
            game_id=game.id,
            bet_amount=game.entry_fee,
            status=game.status,
            winner=winner_name,
            players=players_data,
            total_players=len(players_data),
            created_at=game.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ended=game.ended
        )
        
    except Exception as e:
        logger.error(f"Error getting game details: {e}")
        raise HttpError(500, f"Failed to get game details: {str(e)}")


@game_router.post("/end-game/")
def end_game_endpoint(request, data: WinGameSchema):
    """End a game and optionally set winner"""
    logger.info(f"End game request: {data}")
    
    try:
        # Get the game
        game = get_object_or_404(Game, id=data.game_id)
        logger.info(f"Ending game: {game.id}")
        
        # End the game asynchronously
        end_game.delay(data.game_id, data.playerId)
        
        logger.info(f"Successfully submitted end-game task for game {game.id}")
        return GameSchema(bet_amount=game.entry_fee, game_id=game.id, playerId=data.playerId)
        
    except Exception as e:
        logger.error(f"Error in end_game: {e}")
        raise HttpError(500, f"Failed to end game: {str(e)}")
   