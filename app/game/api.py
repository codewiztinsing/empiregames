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
from .models import Game, GameSettings,GameType
from .tasks import charge_player,push_transaction,update_player_balance
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema,GameSettingsSchema,GameTypeSchema
from ninja.errors import HttpError  # Correct import


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
game_router = Router()
@game_router.post("/update-metrics/")
def update_metrics(request):
    """Persist metrics sent from Node server: real/fake/total players and win amount."""
    try:
        body = json.loads(request.body.decode() or "{}")
        game_id = body.get("game_id")
        if not game_id:
            # For compatibility: accept bet_amount-only, resolve current game
            bet_amount = body.get("bet_amount")
            if bet_amount is None:
                return JsonResponse({"success": False, "error": "game_id or bet_amount required"}, status=400)
            game = Game.objects.filter(entry_fee=bet_amount, ended=False).last()
            if not game:
                return JsonResponse({"success": False, "error": "Game not found for bet_amount"}, status=404)
        else:
            game = get_object_or_404(Game, id=game_id)

        real_players = int(body.get("real_players") or 0)
        fake_players = int(body.get("fake_players") or 0)
        total_players = int(body.get("total_players") or (real_players + fake_players))
        win_amount = float(body.get("win_amount") or 0)

        game.real_players = real_players
        game.fake_players = fake_players
        game.total_players = total_players
        game.total_win_amount = win_amount
        game.started = True
      
        game.save(update_fields=[
            "real_players", "fake_players", "total_players", "total_win_amount", "updated_at","started"
        ])

        return JsonResponse({"success": True, "game_id": game.id}, status=200)
    except Exception as e:
        logger.error(f"update_metrics error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@game_router.post("/join-game/",response=GameSchema)
def join_game(request, data: BetSchema):
    logger.info(f"Join game: {data}")
    game = get_object_or_404(Game,id=data.game_id)
    
    players = data.players
    players_dict = {}
    for player in players:
        players_dict[player.playerId] = player.numberOfBoards
    
    logger.info(f"Players dict: {players_dict}")
    
    # Update game metrics (real/fake/total/win_amount)
    try:
        real_players = len(players_dict.keys())
        total_players = int(data.total_players) if data.total_players is not None else real_players
        fake_players = max(0, total_players - real_players)
        try:
            entry_fee = float(game.entry_fee)
        except Exception:
            entry_fee = 0.0
        total_win_amount = float(total_players) * entry_fee * 0.78

        game.real_players = real_players
        game.fake_players = fake_players
        game.total_players = total_players
        game.total_win_amount = total_win_amount
        game.save(update_fields=[
            "real_players","fake_players","total_players","total_win_amount","updated_at"
        ])
        logger.info(
            f"Updated game {game.id} metrics real={real_players} fake={fake_players} total={total_players} win={total_win_amount}"
        )
    except Exception as e:
        logger.error(f"Failed updating game metrics: {e}")
    
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
        
        # Player statistics (PlayerGame removed); using aggregated totals from Game
        total_players = Game.objects.aggregate(total=Sum('total_players'))['total'] or 0
        active_players_today = Game.objects.filter(
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).aggregate(total=Sum('total_players'))['total'] or 0
        
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
            # Player count from aggregated field
            player_count = game.total_players
            
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
            # Player count for this game
            player_count = game.total_players
            
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
        
        # PlayerGame removed; return recent games as fallback for user
        games = Game.objects.select_related('winner').order_by('-created_at')[:20]
        games_list = []
        for game in games:
            
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
                "has_bingo": False,
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
        games = Game.objects.select_related('winner').order_by('-created_at')[:limit]
        
        games_list = []
        for game in games:
            # PlayerGame removed; omit per-player listing in this view
            players = []
            
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
   