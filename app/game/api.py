import json
import logging
from ninja import Router
from users.models import User
from wallet.models import Wallet
from .models import FakePlayerSettings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from utils.fake_players_factory import count_real_players_in_games
from .tasks import activate_fake_players, deactivate_fake_players
from datetime import timedelta
from .models import Game, GameRoom, PlayerGame, GameSettings, FakePlayerSettings
from .tasks import charge_player,push_transaction,update_player_balance
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema,GameSettingsSchema,GameRoomSchema,GameRoomListSchema
from ninja.errors import HttpError  # Correct import


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
game_router = Router()

@game_router.post("/join-game/",response=GameSchema, auth=None)
def join_game(request, data: BetSchema):
    logger.info(f"Join game: {data}")
    logger.info(f"Join game - total_players: {data.total_players}, fake_players: {data.fake_players}")
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
        fake_players = int(data.fake_players) if data.fake_players is not None else max(0, total_players - real_players)


        
        # Calculate win amount
        try:
            entry_fee = float(game.room.entry_fee)
        except Exception:
            entry_fee = 0.0
        total_win_amount = float(total_players) * entry_fee * 0.78
    
        game.real_players = real_players
        game.fake_players = fake_players
        game.total_players = total_players
        game.total_entry_fees = total_players * game.room.entry_fee
        game.prize_pool = game.total_entry_fees * Decimal('0.78')  # 78% to prize pool
        game.house_edge_amount = game.total_entry_fees * Decimal('0.22')  # 22% house edge
        game.save(update_fields=[
            "real_players","fake_players","total_players","total_entry_fees","prize_pool","house_edge_amount","updated_at"
        ])
        # Activate/deactivate fake players based on real players since last REAL winner
        real_players_count = count_real_players_in_games()
        logger.info(f"Real players since last real-winner game: {real_players_count}")
        fps = FakePlayerSettings.get_solo()
        logger.info(f"Fake player settings: {fps}")
        REAL_PLAYERS_THRESHOLD = int(getattr(fps, 'real_players_threshold', 10) or 10)
        logger.info(f"Real players threshold: {REAL_PLAYERS_THRESHOLD}")
        # Flip condition per requirement: if count > threshold -> ACTIVATE, else DEACTIVATE
        if int(real_players_count or 0) <= REAL_PLAYERS_THRESHOLD:
            logger.info(
                f"Activating fake players (real_players_count {real_players_count} > threshold {REAL_PLAYERS_THRESHOLD})"
            )
            activate_fake_players.delay()
        else:
            logger.info(
                f"Deactivating fake players (real_players_count {real_players_count} <= threshold {REAL_PLAYERS_THRESHOLD})"
            )
            deactivate_fake_players.delay()

        logger.info(
            f"Updated game {game.id} metrics real={real_players} fake={fake_players} total={total_players} win={total_win_amount}"
        )
    except Exception as e:
        logger.error(f"Failed updating game metrics: {e}")
    
    # Log the Celery task call
    logger.info(f"=== CALLING CHARGE_PLAYER CELERY TASK ===")
    logger.info(f"Players dict: {players_dict}")
    logger.info(f"Entry fee: {game.room.entry_fee}")
    logger.info(f"Game ID: {game.id}")
    
    try:
        task_result = charge_player.delay(players_dict, game.room.entry_fee, game.id)
        logger.info(f"Celery task submitted successfully. Task ID: {task_result.id}")
        logger.info(f"Task state: {task_result.state}")
    except Exception as e:
        logger.error(f"Failed to submit charge_player Celery task: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    return GameSchema(bet_amount=game.room.entry_fee, game_id=game.id)    
    
   
    

@game_router.post("/win-game/",response=GameSchema, auth=None)
def win_game(request, data: WinGameSchema):
    logger.info(f"Win game: {data}")
    logger.info(f"Win game - Player: {data.player}, Game ID: {data.game_id}, Win Amount: {data.win_amount}")
    game = get_object_or_404(Game,id=data.game_id)
    player = data.player
    win_amount = data.win_amount
    logger.info(f"Game: {game}")
    logger.info(f"Player: {player}")
    
    # Update game winner and status
    try:
        # For fake players, don't set a real user as winner
        if player != "BOT_FAKE":
            # Try to find the user by telegram_id or player ID
            from users.models import User
            try:
                winner_user = User.objects.get(telegram_id=str(player))
                game.winner = winner_user
                logger.info(f"Set winner: {winner_user.username} (ID: {winner_user.id})")
            except User.DoesNotExist:
                logger.warning(f"User with telegram_id {player} not found, setting winner to None")
                game.winner = None
        else:
            # For fake winners, set winner to None
            game.winner = None
            logger.info("Fake player won, winner set to None")
        
        # Mark game as completed
        game.status = 'completed'
        game.ended_at = timezone.now()
        game.save(update_fields=['winner', 'status', 'ended_at', 'updated_at'])
        logger.info(f"Game {game.id} marked as completed with winner: {game.winner}")
        
    except Exception as e:
        logger.error(f"Error updating game winner: {e}")
    
    # Only update player balance for real players
    if player != "BOT_FAKE":
        update_player_balance.delay(player,win_amount,game.id)
    
    return GameSchema(bet_amount=game.room.entry_fee, game_id=game.id)    

@game_router.get("/next-game/",response=GameSchema, auth=None)
def next_game(request):
    logger.info(f"Next game: {request}")
    bet_amount = request.GET.get("bet_amount")
    # Find game by room's entry_fee
    game = Game.objects.filter(room__entry_fee=bet_amount, ended_at__isnull=True).first()
    logger.info(f"Game: {game}")
    if not game:
        # Find an existing game room with the bet amount, or create a new one
        try:
            # Try to get the first active room with this entry fee
            room = GameRoom.objects.filter(
                entry_fee=bet_amount,
                is_active=True
            ).first()
            
            if not room:
                # Create a new game room if none exists
                room = GameRoom.objects.create(
                    entry_fee=bet_amount,
                    name=f'Room {bet_amount}',
                    room_type='standard',
                    is_active=True
                )
        except Exception as e:
            logger.error(f"Error handling GameRoom for bet_amount {bet_amount}: {e}")
            # Fallback: create a new room
            room = GameRoom.objects.create(
                entry_fee=bet_amount,
                name=f'Room {bet_amount}',
                room_type='standard',
                is_active=True
            )
        
        game = Game.objects.create(room=room)
    logger.info(f"Game: {game}")
  
    return GameSchema(bet_amount=game.room.entry_fee, game_id=game.id)





@game_router.get("/game-settings/",response=GameSettingsSchema, auth=None)
def game_settings(request):
    logger.info(f"Game settings: {request}")
    game_settings = GameSettings.objects.first()
    if not game_settings:
        game_settings = GameSettings.objects.create(game_speed=5000,count_down_time=30)
    
    # Get fake player settings with error handling
    try:
        fake_settings = FakePlayerSettings.get_solo()
        logger.info(f"Fake player settings loaded: {fake_settings}")
    except Exception as e:
        logger.error(f"Error loading fake player settings: {e}")
        # Create default fake player settings if none exist
        fake_settings = FakePlayerSettings.objects.create(
            max_fake_players=50,
            calls_before_fake_winner=10,
            real_players_threshold=10,
            fake_players_can_win=True
        )
        logger.info(f"Created default fake player settings: {fake_settings}")
    
    return GameSettingsSchema(
        game_speed=game_settings.game_speed,
        count_down_time=game_settings.count_down_time,
        max_fake_players=fake_settings.max_fake_players,
        calls_before_fake_winner=fake_settings.calls_before_fake_winner,
        real_players_threshold=fake_settings.real_players_threshold,
        fake_players_can_win=fake_settings.fake_players_can_win
    )


@game_router.get("/game-rooms/", response=GameRoomListSchema)
def game_rooms(request):
    logger.info(f"Game rooms: {request}")
    game_rooms = GameRoom.objects.filter(is_active=True).order_by('entry_fee')
    return GameRoomListSchema(game_rooms=game_rooms)


@game_router.get("/fake-player-settings/", auth=None)
def get_fake_player_settings(request):
    """Get fake player settings for dynamic control"""
    try:
        from .models import FakePlayerSettings
        settings = FakePlayerSettings.get_solo()
        return JsonResponse({
            "max_fake_players": settings.max_fake_players,
            "calls_before_fake_winner": settings.calls_before_fake_winner,
            "real_players_threshold": settings.real_players_threshold,
            "fake_players_can_win": settings.fake_players_can_win,
            "updated_at": settings.updated_at.isoformat()
        }, status=200)
    except Exception as e:
        logger.error(f"Error getting fake player settings: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# Games Dashboard API Endpoints
@game_router.get("/games/stats/")
def get_games_stats(request):
    """Get games statistics for dashboard"""
    try:
        # Get data for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Game statistics
        total_games = Game.objects.count()
        active_games = Game.objects.filter(ended_at__isnull=True).count()
        completed_today = Game.objects.filter(ended_at__isnull=False, created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).count()
        completed_last_30_days = Game.objects.filter(ended_at__isnull=False, created_at__gte=thirty_days_ago).count()
        
        # Revenue calculations
        total_revenue = Game.objects.filter(ended_at__isnull=False).aggregate(Sum('total_entry_fees'))['total_entry_fees__sum'] or 0
        revenue_last_30_days = Game.objects.filter(ended_at__isnull=False, created_at__gte=thirty_days_ago).aggregate(Sum('total_entry_fees'))['total_entry_fees__sum'] or 0
        
        # Player statistics (PlayerGame removed); using aggregated totals from Game
        total_players = Game.objects.aggregate(total=Sum('total_players'))['total'] or 0
        active_players_today = Game.objects.filter(
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).aggregate(total=Sum('total_players'))['total'] or 0
        
        # Win statistics
        games_with_winners = Game.objects.filter(ended_at__isnull=False, winner__isnull=False).count()
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
            elif game.status == 'completed' and not game.winner:
                winner_info = {
                    "id": None,
                    "username": "Fake Player",
                    "phone": None,
                    "telegram_id": "BOT_FAKE"
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": bool(game.started_at),
                "ended": game.ended_at is not None,
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
            elif game.status == 'completed' and not game.winner:
                winner_info = {
                    "id": None,
                    "username": "Fake Player",
                    "phone": None,
                    "telegram_id": "BOT_FAKE"
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": bool(game.started_at),
                "ended": game.ended_at is not None,
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
            elif game.status == 'completed' and not game.winner:
                winner_info = {
                    "id": None,
                    "username": "Fake Player",
                    "phone": None,
                    "telegram_id": "BOT_FAKE"
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": bool(game.started_at),
                "ended": game.ended_at is not None,
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
            elif game.status == 'completed' and not game.winner:
                winner_info = {
                    "id": None,
                    "username": "Fake Player",
                    "phone": None,
                    "telegram_id": "BOT_FAKE"
                }
            
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": bool(game.started_at),
                "ended": game.ended_at is not None,
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
   