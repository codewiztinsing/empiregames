import jwt
from ninja import NinjaAPI,Router
from ninja.security import django_auth
from .auth import encode_jwt,decode_jwt
from .schema import RegisterSchema, LoginSchema, UserSchema, UserResponseSchema
# from .models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from users.models import User
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.conf import settings
from wallet.models import Transaction,ChapaSession,Wallet,WithdrawalRequest
from game.models import Game, PlayerGame
from django.db.models import Sum, Count, Q
from django.utils import timezone


from pydantic import BaseModel
from typing import Optional, Union

users_router = Router()



@users_router.get("/refresh-token")
def refresh_access_token(request):
    return {"token": request.auth}



@users_router.post("/register")
def register(request, data: RegisterSchema):
    try:
        print("data = ",data)
        # Check if user already exists
        if User.objects.filter(phone=data.phone).exists():
            return JsonResponse({
                "success": False,
                "message": "Phone number already registered"
            }, status=400)
        
        # Check if username already exists
        if User.objects.filter(username=data.username).exists():
            return JsonResponse({
                "success": False,
                "message": "Username already taken"
            }, status=400)

        
        referred_by = None
        print("referral id ",data.referred_by)
        if data.referred_by:
            referred_by = User.objects.get(telegram_id=data.referred_by)

            print("referred_by = ",referred_by)
        else:
            data.referred_by = None

    
        # Create user with hashed password
        created_user, created = User.objects.get_or_create(
            username=data.username,
            phone=data.phone,
            telegram_id=data.telegram_id,
            referred_by=referred_by,
            password=make_password(data.password)
        )
        print("created_user = ",created_user)
        
        if created_user:
            return JsonResponse({
                "success": True,
                "message": "User registered successfully",
                "username": created_user.username,
                "phone": created_user.phone,
                "telegram_id": created_user.telegram_id
            }, status=200)
        else:
            print("user registration failed")
            return JsonResponse({
                "success": False,
                "message": "User registration failed"
            }, status=400)
        
        
    except Exception as e:
        print("error = ",e)
        return JsonResponse({
            "success": False,
            "message": f"Registration failed: {str(e)}"
        }, status=500)



@users_router.post("/login")
def login(request, data: LoginSchema):
    try:
        user = User.objects.get(username=data.username)
        pasword = make_password(data.password)
        print("pasword = ",pasword)
        print("user.password = ",user.password)
      
        
        if pasword == user.password:
            # Generate JWT token
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(days=1),  # 1 day expiry
                'iat': datetime.utcnow()
            }
            
            print("user.password = ",user.password)
            token = jwt.encode(
                payload, 
                settings.SECRET_KEY, 
                algorithm='HS256'
            )
            print("token = ",token)
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone": user.phone
                }
            }
        else:
            return {"success": False, "message": "Invalid credentials"}
            
    except Exception as e:
        return {"success": False, "message": "Login failed"}


# get user by telegram id
@users_router.get("/{telegram_id}",response=UserResponseSchema)
def get_user_by_telegram_id(request,telegram_id:int):
    try:
        from datetime import datetime, timedelta

        user = User.objects.get(telegram_id=str(telegram_id))
        # Get the start and end of the current week (Monday to Sunday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        games_played_this_week = Transaction.objects.filter(
            user=user,
            type="BET",
            created_at__date__gte=start_of_week,
            created_at__date__lte=end_of_week
        ).count()
        print("games_played_this_week remaining = ", games_played_this_week)
        print("27-games_played_this_week = ",27-games_played_this_week)
        return UserResponseSchema(
            success=True,
            username=user.username,
            email=user.email,
            phone=user.phone,
            telegram_id=user.telegram_id,
            games_played_this_week=games_played_this_week,
            remaining_games=27-games_played_this_week
        )
    except Exception as e:
        print("error = ",e)
        return UserResponseSchema(success=False, message="User not found")


@users_router.get("/{user_id}/daily-withdraw-limit")
def get_daily_withdraw_limit(request,user_id:int):
    try:
        user = User.objects.get(telegram_id=user_id)
        today = datetime.now().date()
        transactions = Transaction.objects.filter(user=user,type="WITHDRAW",created_at__date=today)
        daily_withdraw_limit = len(transactions)
        return {"daily_withdraw_limit": daily_withdraw_limit}
    except Exception as e:
        print("error = ",e)
        return {"success": False, "message": "Failed to get daily withdraw limit"}


@users_router.get("/{user_id}/number-of-game-played")
def get_number_of_game_played(request,user_id:int):
    try:
        print("user_id = ",user_id)
        user = User.objects.get(telegram_id=user_id)
        print("user = ",user)
        transactions = Transaction.objects.filter(user=user,type="BET")
        print("transactions = ",transactions)
        number_of_game_played = transactions.count()
        print("number_of_game_played = ",number_of_game_played)
        return {"number_of_game_played": number_of_game_played}
    except Exception as e:
        return {"success": False, "message": "Failed to get number of game played"}
    

@users_router.get("/{user_id}/number-of-game-won")
def get_number_of_game_won(request,user_id:int):
    try:
        user = User.objects.get(telegram_id=user_id)
        number_of_game_won = Transaction.objects.filter(user=user,type="WIN").count()
        return {"number_of_game_won": number_of_game_won}
    except Exception as e:
        return {"success": False, "message": "Failed to get number of game won"}    
# is deposited user
@users_router.get("/{user_id}/is-deposited")
def is_deposited(request, user_id: int):
    try:
        user = User.objects.get(telegram_id=user_id)
        print("phone ",user.phone)
        print("user ",user)
        # Check if user has any successful deposit transactions via ChapaSession
        has_deposited = ChapaSession.objects.filter(
            phone_number=user.phone)

        print("has deposited ",has_deposited)
        has_deposited = ChapaSession.objects.filter(
            phone_number=user.phone,
            status='success'
        ).exists()

        return {"is_deposited": has_deposited}
    except User.DoesNotExist:
        return {"success": False, "message": "User not found"}
    except Exception as e:
        print("error ",e)
        return {"success": False, "message": "Failed to check deposit status"}


# User Detail API Endpoints
@users_router.get("/{user_id}/details/")
def get_user_details(request, user_id: int):
    """Get comprehensive user details including wallet and transaction info"""
    try:
        user = User.objects.get(id=user_id)
        
        # Get wallet information
        try:
            wallet = Wallet.objects.get(user=user)
            wallet_balance = float(wallet.balance)
        except Wallet.DoesNotExist:
            wallet_balance = 0.0
        
        # Get transaction statistics
        total_deposits = Transaction.objects.filter(user=user, type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'] or 0
        total_withdrawals = Transaction.objects.filter(user=user, type='WITHDRAW').aggregate(Sum('amount'))['amount__sum'] or 0
        total_bets = Transaction.objects.filter(user=user, type='BET').aggregate(Sum('amount'))['amount__sum'] or 0
        total_wins = Transaction.objects.filter(user=user, type='WIN').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get transaction counts
        deposit_count = Transaction.objects.filter(user=user, type='DEPOSIT').count()
        withdrawal_count = Transaction.objects.filter(user=user, type='WITHDRAW').count()
        bet_count = Transaction.objects.filter(user=user, type='BET').count()
        win_count = Transaction.objects.filter(user=user, type='WIN').count()
        
        # Get recent transactions
        recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
        transactions_list = []
        for transaction in recent_transactions:
            transactions_list.append({
                "id": transaction.id,
                "type": transaction.type,
                "amount": float(transaction.amount),
                "status": transaction.status,
                "reference": transaction.reference,
                "created_at": transaction.created_at.isoformat()
            })
        
        # Get withdrawal requests
        withdrawal_requests = WithdrawalRequest.objects.filter(user=user).order_by('-created_at')[:5]
        withdrawal_requests_list = []
        for request in withdrawal_requests:
            withdrawal_requests_list.append({
                "id": request.id,
                "amount": float(request.amount),
                "status": request.status,
                "admin_notes": request.admin_notes,
                "created_at": request.created_at.isoformat(),
                "processed_at": request.processed_at.isoformat() if request.processed_at else None
            })
        
        # Get game statistics
        games_played = PlayerGame.objects.filter(user=user).count()
        games_won = PlayerGame.objects.filter(user=user, has_bingo=True).count()
        total_games_played = user.total_games_played
        games_played_today = user.games_played_today
        games_played_this_week = user.games_played_this_week
        
        # Get recent games
        recent_games = PlayerGame.objects.filter(user=user).select_related('game').order_by('-game__created_at')[:10]
        games_list = []
        for player_game in recent_games:
            game = player_game.game
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "has_bingo": player_game.has_bingo,
                "created_at": game.created_at.isoformat(),
                "ended": game.ended
            })
        
        # Get referral information
        total_referrals = User.objects.filter(referred_by=user).count()
        total_referral_earnings = float(user.total_referral_earnings)
        
        return JsonResponse({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat(),
                "referral_code": user.referral_code,
                "is_agent": user.is_agent,
                "sponsor_changed": user.sponsor_changed
            },
            "wallet": {
                "balance": wallet_balance
            },
            "transactions": {
                "total_deposits": float(total_deposits),
                "total_withdrawals": float(total_withdrawals),
                "total_bets": float(total_bets),
                "total_wins": float(total_wins),
                "deposit_count": deposit_count,
                "withdrawal_count": withdrawal_count,
                "bet_count": bet_count,
                "win_count": win_count,
                "recent_transactions": transactions_list
            },
            "withdrawal_requests": withdrawal_requests_list,
            "games": {
                "total_games_played": total_games_played,
                "games_played_today": games_played_today,
                "games_played_this_week": games_played_this_week,
                "games_won": games_won,
                "recent_games": games_list
            },
            "referrals": {
                "total_referrals": total_referrals,
                "total_earnings": total_referral_earnings
            }
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print(f"Error getting user details: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@users_router.get("/{user_id}/transactions/")
def get_user_transactions(request, user_id: int, limit: int = 20, transaction_type: str = None):
    """Get user transactions with optional filtering"""
    try:
        user = User.objects.get(id=user_id)
        
        transactions = Transaction.objects.filter(user=user)
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)
        
        transactions = transactions.order_by('-created_at')[:limit]
        
        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                "id": transaction.id,
                "type": transaction.type,
                "amount": float(transaction.amount),
                "status": transaction.status,
                "reference": transaction.reference,
                "created_at": transaction.created_at.isoformat()
            })
        
        return JsonResponse({
            "transactions": transactions_list,
            "count": len(transactions_list),
            "user_id": user_id,
            "transaction_type": transaction_type or "all"
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print(f"Error getting user transactions: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@users_router.get("/{user_id}/games/")
def get_user_games(request, user_id: int, limit: int = 20):
    """Get user games history"""
    try:
        user = User.objects.get(id=user_id)
        
        player_games = PlayerGame.objects.filter(user=user).select_related('game').order_by('-game__created_at')[:limit]
        
        games_list = []
        for player_game in player_games:
            game = player_game.game
            games_list.append({
                "id": game.id,
                "entry_fee": float(game.entry_fee),
                "status": game.status,
                "started": game.started,
                "ended": game.ended,
                "has_bingo": player_game.has_bingo,
                "created_at": game.created_at.isoformat(),
                "winner": {
                    "id": game.winner.id,
                    "username": game.winner.username,
                    "phone": game.winner.phone,
                    "telegram_id": game.winner.telegram_id
                } if game.winner else None
            })
        
        return JsonResponse({
            "games": games_list,
            "count": len(games_list),
            "user_id": user_id
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print(f"Error getting user games: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@users_router.get("/{user_id}/wallet/")
def get_user_wallet(request, user_id: int):
    """Get user wallet information"""
    try:
        user = User.objects.get(id=user_id)
        
        try:
            wallet = Wallet.objects.get(user=user)
            wallet_data = {
                "balance": float(wallet.balance),
                "created_at": wallet.created_at.isoformat()
            }
        except Wallet.DoesNotExist:
            wallet_data = {
                "balance": 0.0,
                "created_at": None
            }
        
        # Get transaction summary
        total_deposits = Transaction.objects.filter(user=user, type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'] or 0
        total_withdrawals = Transaction.objects.filter(user=user, type='WITHDRAW').aggregate(Sum('amount'))['amount__sum'] or 0
        total_bets = Transaction.objects.filter(user=user, type='BET').aggregate(Sum('amount'))['amount__sum'] or 0
        total_wins = Transaction.objects.filter(user=user, type='WIN').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return JsonResponse({
            "wallet": wallet_data,
            "summary": {
                "total_deposits": float(total_deposits),
                "total_withdrawals": float(total_withdrawals),
                "total_bets": float(total_bets),
                "total_wins": float(total_wins),
                "net_balance": float(total_deposits + total_wins - total_withdrawals - total_bets)
            },
            "user_id": user_id
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print(f"Error getting user wallet: {e}")
        return JsonResponse({"error": str(e)}, status=500)


