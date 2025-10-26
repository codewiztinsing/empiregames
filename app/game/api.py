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
from .models import Game, GameRoom, PlayerGame, GameSettings, FakePlayerSettings, CustomBingoCard
from .tasks import charge_player,push_transaction,update_player_balance
from .schema import BetSchema,GameSchema,NextGameSchema,WinGameSchema,GameSettingsSchema,GameRoomSchema,GameRoomListSchema,CustomCardSchema
from ninja.errors import HttpError  # Correct import
from django.core.exceptions import ValidationError


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
        game_settings = GameSettings.objects.create(
            default_game_speed=5000,
            default_countdown_duration=30
        )
    
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
        game_speed=game_settings.default_game_speed,
        count_down_time=game_settings.default_countdown_duration,
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
                "entry_fee": float(game.room.entry_fee),
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
                "entry_fee": float(game.room.entry_fee),
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
                "entry_fee": float(game.room.entry_fee),
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
                "entry_fee": float(game.room.entry_fee),
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


# Custom Bingo Card API Endpoints
@game_router.get("/custom-cards/", auth=None)
def get_user_custom_cards(request, telegram_id: str):
    """Get all custom cards for a user"""
    try:
        from django.conf import settings
        
        # In development mode, create a test user if it doesn't exist
        if getattr(settings, 'DEBUG', False):
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': f'test_user_{telegram_id}',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'phone': '1234567890'
                }
            )
            if created:
                logger.info(f"Created test user for telegram_id: {telegram_id}")
        else:
            user = get_object_or_404(User, telegram_id=telegram_id)
        
        cards = CustomBingoCard.get_user_cards(user)
        
        cards_list = []
        for card in cards:
            cards_list.append({
                "id": card.id,
                "name": card.name,
                "is_default": card.is_default,
                "numbers": card.get_card_numbers(),
                "created_at": card.created_at.isoformat(),
                "updated_at": card.updated_at.isoformat()
            })
        
        return JsonResponse({
            "cards": cards_list,
            "count": len(cards_list)
        }, status=200)
    except Exception as e:
        logger.error(f"Error getting custom cards: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/custom-cards/default/", auth=None)
def get_user_default_card(request, telegram_id: str):
    """Get user's default custom card"""
    try:
        from django.conf import settings
        
        # In development mode, create a test user if it doesn't exist
        if getattr(settings, 'DEBUG', False):
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': f'test_user_{telegram_id}',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'phone': '1234567890'
                }
            )
            if created:
                logger.info(f"Created test user for telegram_id: {telegram_id}")
        else:
            user = get_object_or_404(User, telegram_id=telegram_id)
        
        card = CustomBingoCard.get_user_default_card(user)
        
        if card:
            return JsonResponse({
                "card": {
                    "id": card.id,
                    "name": card.name,
                    "is_default": card.is_default,
                    "numbers": card.get_card_numbers(),
                    "created_at": card.created_at.isoformat(),
                    "updated_at": card.updated_at.isoformat()
                }
            }, status=200)
        else:
            return JsonResponse({
                "card": None,
                "message": "No default card found"
            }, status=200)
    except Exception as e:
        logger.error(f"Error getting default card: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.post("/custom-cards/create/", auth=None)
def create_custom_card(request, data: CustomCardSchema):
    """Create a new custom bingo card"""
    try:
        logger.info("🎯 [CreateCard] Starting card creation")
        from django.conf import settings
        
        # Extract data from schema
        telegram_id = data.telegram_id
        numbers = data.numbers
        is_default = data.is_default
        
        logger.info(f"📝 [CreateCard] Received data - telegram_id: {telegram_id}, is_default: {is_default}")
        logger.info(f"📝 [CreateCard] Numbers type: {type(numbers)}, keys: {numbers.keys() if isinstance(numbers, dict) else 'Not a dict'}")
        
        # In development mode, create a test user if it doesn't exist
        if getattr(settings, 'DEBUG', False):
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': f'test_user_{telegram_id}',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'phone': '1234567890'
                }
            )
            if created:
                logger.info(f"Created test user for telegram_id: {telegram_id}")
        else:
            user = get_object_or_404(User, telegram_id=telegram_id)
        
        # Validate numbers format
        if not isinstance(numbers, dict):
            logger.error(f"❌ [CreateCard] Numbers is not a dictionary: {type(numbers)}")
            return JsonResponse({"error": "Numbers must be a dictionary"}, status=400)
        
        logger.info(f"✅ [CreateCard] Numbers validated as dictionary")
        
        # Limit one card per user
        existing_cards_count = CustomBingoCard.objects.filter(user=user).count()
        logger.info(f"📊 [CreateCard] User has {existing_cards_count} existing cards")
        if existing_cards_count >= 1:
            logger.warning(f"⚠️ [CreateCard] User already has {existing_cards_count} card(s), rejecting")
            return JsonResponse({
                "error": "You can only have one custom card. Please delete your existing card to create a new one.",
                "validation_errors": ["maximum_card_limit_reached"]
            }, status=400)
        
        # Check if user already has a card with these exact numbers
        if CustomBingoCard.objects.filter(user=user, numbers=numbers).exists():
            return JsonResponse({"error": "A card with these numbers already exists"}, status=400)
        
        # Validate card structure before creating
        logger.info("🔍 [CreateCard] Starting validation")
        try:
            # Check if all required columns are present
            required_columns = ['B', 'I', 'N', 'G', 'O']
            validation_errors = []
            
            logger.info(f"🔍 [CreateCard] Checking columns: {list(numbers.keys())}")
            
            for column in required_columns:
                if column not in numbers:
                    logger.error(f"❌ [CreateCard] Missing column: {column}")
                    validation_errors.append(f"missing_column_{column}")
                    continue
                
                if not isinstance(numbers[column], list) or len(numbers[column]) != 5:
                    logger.error(f"❌ [CreateCard] Column {column} invalid - Type: {type(numbers[column])}, Length: {len(numbers[column]) if isinstance(numbers[column], list) else 'N/A'}")
                    validation_errors.append(f"invalid_column_length_{column}")
                    continue
                
                logger.info(f"✅ [CreateCard] Column {column} validated - 5 numbers present")
            
            # Validate number ranges if structure is valid
            if not validation_errors:
                column_ranges = {
                    'B': (1, 15),
                    'I': (16, 30),
                    'N': (31, 45),
                    'G': (46, 60),
                    'O': (61, 75)
                }
                
                all_numbers = []
                for column, nums in numbers.items():
                    if column not in column_ranges:
                        continue
                    min_val, max_val = column_ranges[column]
                    for number in nums:
                        if not isinstance(number, int) or number < min_val or number > max_val:
                            validation_errors.append(f"invalid_range_{column}")
                            break
                        all_numbers.append(number)
                
                # Check for duplicates
                if len(all_numbers) != len(set(all_numbers)):
                    validation_errors.append("duplicate_numbers")
            
            # Return validation errors if any
            if validation_errors:
                logger.error(f"❌ [CreateCard] Validation failed with errors: {validation_errors}")
                error_messages = {
                    "missing_column_B": "Column B is missing",
                    "missing_column_I": "Column I is missing",
                    "missing_column_N": "Column N is missing",
                    "missing_column_G": "Column G is missing",
                    "missing_column_O": "Column O is missing",
                    "invalid_column_length_B": "Column B must have exactly 5 numbers",
                    "invalid_column_length_I": "Column I must have exactly 5 numbers",
                    "invalid_column_length_N": "Column N must have exactly 5 numbers",
                    "invalid_column_length_G": "Column G must have exactly 5 numbers",
                    "invalid_column_length_O": "Column O must have exactly 5 numbers",
                    "invalid_range_B": "Numbers in column B must be between 1 and 15",
                    "invalid_range_I": "Numbers in column I must be between 16 and 30",
                    "invalid_range_N": "Numbers in column N must be between 31 and 45",
                    "invalid_range_G": "Numbers in column G must be between 46 and 60",
                    "invalid_range_O": "Numbers in column O must be between 61 and 75",
                    "duplicate_numbers": "Duplicate numbers found in the card"
                }
                messages = [error_messages.get(e, e) for e in validation_errors]
                return JsonResponse({
                    "error": "; ".join(messages),
                    "validation_errors": validation_errors
                }, status=400)
                
        except Exception as ve:
            return JsonResponse({
                "error": f"Validation error: {str(ve)}",
                "validation_errors": ["validation_failed"]
            }, status=400)
        
        # Generate a card identifier from the numbers
        card_identifier = f"Card-{hash(str(numbers)) % 10000:04d}"
        
        logger.info(f"🎨 [CreateCard] Creating card with identifier: {card_identifier}")
        
        # Create the card
        card = CustomBingoCard(
            user=user,
            name=card_identifier,  # Use generated identifier
            numbers=numbers,
            is_default=is_default
        )
        
        try:
            card.full_clean()  # This will call the clean() method
            logger.info(f"✅ [CreateCard] Card validation passed, saving...")
            card.save()
            logger.info(f"✅ [CreateCard] Card saved successfully with ID: {card.id}")
            
            # If this is set as default, unset others
            if is_default:
                CustomBingoCard.set_default_card(user, card.id)
            
            # Send notification to user via Telegram (async)
            try:
                import asyncio
                from telegram import Bot
                from core.settings import TELEGRAM_BOT_TOKEN
                
                async def send_notification():
                    bot = Bot(token=TELEGRAM_BOT_TOKEN)
                    message = (
                        f"🎉 Custom Bingo Card Created!\n\n"
                        f"Your custom card has been saved successfully.\n"
                        f"Card ID: {card.id}\n\n"
                        f"Use this card in your next games!"
                    )
                    await bot.send_message(chat_id=int(telegram_id), text=message)
                    logger.info(f"Sent notification to user {telegram_id}")
                
                # Run async notification
                asyncio.create_task(send_notification())
            except Exception as notify_error:
                logger.warning(f"Failed to send notification: {notify_error}")
            
            return JsonResponse({
                "card": {
                    "id": card.id,
                    "name": card.name,
                    "is_default": card.is_default,
                    "numbers": card.get_card_numbers(),
                    "created_at": card.created_at.isoformat(),
                    "updated_at": card.updated_at.isoformat()
                },
                "message": "Card created successfully"
            }, status=201)
        except ValidationError as ve:
            logger.error(f"❌ [CreateCard] ValidationError: {str(ve)}")
            return JsonResponse({"error": str(ve)}, status=400)
            
    except Exception as e:
        logger.error(f"❌ [CreateCard] Exception creating custom card: {str(e)}")
        import traceback
        logger.error(f"❌ [CreateCard] Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.get("/custom-cards/generate-random-card/", auth=None)
def generate_random_card(request, telegram_id: str):
    """Generate a random bingo card for preview"""
    try:
        import random
        
        # Column ranges
        column_ranges = {
            'B': (1, 15),
            'I': (16, 30),
            'N': (31, 45),
            'G': (46, 60),
            'O': (61, 75)
        }
        
        numbers = {}
        for column, (min_val, max_val) in column_ranges.items():
            # Generate 5 unique random numbers for this column
            column_numbers = []
            while len(column_numbers) < 5:
                num = random.randint(min_val, max_val)
                if num not in column_numbers:
                    column_numbers.append(num)
            numbers[column] = sorted(column_numbers)
        
        return JsonResponse({
            "numbers": numbers,
            "message": "Random card generated successfully"
        }, status=200)
    except Exception as e:
        logger.error(f"Error generating random card: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.put("/custom-cards/{card_id}/", auth=None)
def update_custom_card(request, card_id: int, telegram_id: str, name: str = None, numbers: dict = None, is_default: bool = None):
    """Update an existing custom bingo card"""
    try:
        user = get_object_or_404(User, telegram_id=telegram_id)
        card = get_object_or_404(CustomBingoCard, id=card_id, user=user)
        
        # Update fields if provided
        if name is not None:
            # Check if another card with this name exists
            if CustomBingoCard.objects.filter(user=user, name=name).exclude(id=card_id).exists():
                return JsonResponse({"error": "A card with this name already exists"}, status=400)
            card.name = name
        
        if numbers is not None:
            card.numbers = numbers
        
        if is_default is not None:
            card.is_default = is_default
        
        try:
            card.full_clean()  # This will call the clean() method
            card.save()
            
            # If this is set as default, unset others
            if is_default:
                CustomBingoCard.set_default_card(user, card.id)
            
            return JsonResponse({
                "card": {
                    "id": card.id,
                    "name": card.name,
                    "is_default": card.is_default,
                    "numbers": card.get_card_numbers(),
                    "created_at": card.created_at.isoformat(),
                    "updated_at": card.updated_at.isoformat()
                },
                "message": "Card updated successfully"
            }, status=200)
        except ValidationError as ve:
            return JsonResponse({"error": str(ve)}, status=400)
            
    except Exception as e:
        logger.error(f"Error updating custom card: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.delete("/custom-cards/{card_id}/", auth=None)
def delete_custom_card(request, card_id: int, telegram_id: str):
    """Delete a custom bingo card"""
    try:
        user = get_object_or_404(User, telegram_id=telegram_id)
        card = get_object_or_404(CustomBingoCard, id=card_id, user=user)
        
        card_name = card.name
        card.delete()
        
        return JsonResponse({
            "message": f"Card '{card_name}' deleted successfully"
        }, status=200)
    except Exception as e:
        logger.error(f"Error deleting custom card: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@game_router.post("/custom-cards/{card_id}/set-default/", auth=None)
def set_default_card(request, card_id: int, telegram_id: str):
    """Set a custom card as default"""
    try:
        user = get_object_or_404(User, telegram_id=telegram_id)
        card = get_object_or_404(CustomBingoCard, id=card_id, user=user)
        
        CustomBingoCard.set_default_card(user, card_id)
        
        return JsonResponse({
            "message": f"Card '{card.name}' set as default successfully"
        }, status=200)
    except Exception as e:
        logger.error(f"Error setting default card: {e}")
        return JsonResponse({"error": str(e)}, status=500)


   