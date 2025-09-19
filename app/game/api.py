import json
import logging
from ninja import Router
from users.models import User
from wallet.models import Wallet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Game, PlayerGame,GameSettings,GameType
from .tasks import charge_player,push_transaction,update_player_balance
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema,GameSettingsSchema,GameTypeSchema
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


@game_router.get("/game-settings/",response=GameSettingsSchema)
def game_settings(request):
    logger.info(f"Game settings: {request}")
    game_settings = GameSettings.objects.first()
    if not game_settings:
        game_settings = GameSettings.objects.create(game_speed=5000,count_down_time=30)
    return GameSettingsSchema(game_speed=game_settings.game_speed,count_down_time=game_settings.count_down_time)


@game_router.get("/game-types/",response=GameTypeSchema)
def game_types(request):
    logger.info(f"Game types: {request}")
    game_types = GameType.objects.all().order_by('-id')
    return GameTypeSchema(game_types=game_types)


# Games Dashboard API Endpoints
@game_router.get("/games/stats/")
def get_games_stats(request):
    """Get games statistics for dashboard"""
    try:
        # Get data for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Game statistics
        total_games = Game.objects.count()
        active_games = Game.objects.filter(ended=False).count()
        completed_today = Game.objects.filter(ended=True, created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).count()
        completed_last_30_days = Game.objects.filter(ended=True, created_at__gte=thirty_days_ago).count()
        
        # Revenue calculations
        total_revenue = Game.objects.filter(ended=True).aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
        revenue_last_30_days = Game.objects.filter(ended=True, created_at__gte=thirty_days_ago).aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
        
        # Player statistics
        total_players = PlayerGame.objects.values('user').distinct().count()
        active_players_today = PlayerGame.objects.filter(
            game__created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).values('user').distinct().count()
        
        # Win statistics
        games_with_winners = Game.objects.filter(ended=True, winner__isnull=False).count()
        win_rate = (games_with_winners / completed_last_30_days * 100) if completed_last_30_days > 0 else 0
        
        return JsonResponse({
            "total_games": total_games,
            "active_games": active_games,
            "completed_today": completed_today,
            "completed_last_30_days": completed_last_30_days,
            "total_revenue": float(total_revenue),
            "revenue_last_30_days": float(revenue_last_30_days),
            "total_players": total_players,
            "active_players_today": active_players_today,
            "games_with_winners": games_with_winners,
            "win_rate": round(win_rate, 1),
            "period": "last_30_days",
            "date_range": {
                "from": thirty_days_ago.strftime('%m/%d/%Y'),
                "to": timezone.now().strftime('%m/%d/%Y')
            }
        }, status=200)
    except Exception as e:
        print(f"Error getting games stats: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/games/recent/")
def get_recent_games(request, limit: int = 20):
    """Get recent games with player information"""
    try:
        games = Game.objects.select_related('winner').order_by('-created_at')[:limit]
        
        games_list = []
        for game in games:
            # Get player count for this game
            player_count = PlayerGame.objects.filter(game=game).count()
            
            # Get winner info
            winner_info = None
            if game.winner:
                winner_info = {
                    "id": game.winner.id,
                    "username": game.winner.username,
                    "phone": game.winner.phone,
                    "telegram_id": game.winner.telegram_id
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": game.started,
                "ended": game.ended,
                "player_count": player_count,
                "winner": winner_info,
                "created_at": game.created_at.isoformat(),
                "players": game.players if game.players else []
            })
        
        return JsonResponse({
            "games": games_list,
            "count": len(games_list)
        }, status=200)
    except Exception as e:
        print(f"Error getting recent games: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/games/by-status/")
def get_games_by_status(request, status: str = None):
    """Get games filtered by status"""
    try:
        if status:
            games = Game.objects.filter(status=status).select_related('winner').order_by('-created_at')
        else:
            games = Game.objects.select_related('winner').order_by('-created_at')
        
        games_list = []
        for game in games:
            # Get player count for this game
            player_count = PlayerGame.objects.filter(game=game).count()
            
            # Get winner info
            winner_info = None
            if game.winner:
                winner_info = {
                    "id": game.winner.id,
                    "username": game.winner.username,
                    "phone": game.winner.phone,
                    "telegram_id": game.winner.telegram_id
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": game.started,
                "ended": game.ended,
                "player_count": player_count,
                "winner": winner_info,
                "created_at": game.created_at.isoformat(),
                "players": game.players if game.players else []
            })
        
        return JsonResponse({
            "games": games_list,
            "count": len(games_list),
            "status": status or "all"
        }, status=200)
    except Exception as e:
        print(f"Error getting games by status: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/games/by-user/")
def get_games_by_user(request, user_id: int = None, telegram_id: str = None):
    """Get games for a specific user"""
    try:
        if user_id:
            user = get_object_or_404(User, id=user_id)
        elif telegram_id:
            user = get_object_or_404(User, telegram_id=telegram_id)
        else:
            return JsonResponse({"error": "Either user_id or telegram_id is required"}, status=400)
        
        # Get games where user participated
        player_games = PlayerGame.objects.filter(user=user).select_related('game', 'game__winner')
        
        games_list = []
        for player_game in player_games:
            game = player_game.game
            
            # Get winner info
            winner_info = None
            if game.winner:
                winner_info = {
                    "id": game.winner.id,
                    "username": game.winner.username,
                    "phone": game.winner.phone,
                    "telegram_id": game.winner.telegram_id
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": game.started,
                "ended": game.ended,
                "has_bingo": player_game.has_bingo,
                "winner": winner_info,
                "created_at": game.created_at.isoformat(),
                "players": game.players if game.players else []
            })
        
        return JsonResponse({
            "games": games_list,
            "count": len(games_list),
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "telegram_id": user.telegram_id
            }
        }, status=200)
    except Exception as e:
        print(f"Error getting games by user: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/games/detailed/")
def get_detailed_games(request, limit: int = 20):
    """Get detailed games information with all related data"""
    try:
        games = Game.objects.select_related('winner').prefetch_related('playergame_set__user').order_by('-created_at')[:limit]
        
        games_list = []
        for game in games:
            # Get all players for this game
            players = []
            for player_game in game.playergame_set.all():
                players.append({
                    "id": player_game.user.id,
                    "username": player_game.user.username,
                    "phone": player_game.user.phone,
                    "telegram_id": player_game.user.telegram_id,
                    "has_bingo": player_game.has_bingo
                })
            
            # Get winner info
            winner_info = None
            if game.winner:
                winner_info = {
                    "id": game.winner.id,
                    "username": game.winner.username,
                    "phone": game.winner.phone,
                    "telegram_id": game.winner.telegram_id
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": game.started,
                "ended": game.ended,
                "player_count": len(players),
                "players": players,
                "winner": winner_info,
                "created_at": game.created_at.isoformat(),
                "raw_players": game.players if game.players else []
            })
        
        return JsonResponse({
            "games": games_list,
            "count": len(games_list)
        }, status=200)
    except Exception as e:
        print(f"Error getting detailed games: {e}")
        return JsonResponse({"error": str(e)}, status=500)
   