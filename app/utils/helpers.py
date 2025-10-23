import requests
from decouple import config
import os
import django
from django.conf import settings
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django models
from users.models import User
from wallet.models import Wallet, Transaction, WithdrawalRequest, PaymentSettings
from game.models import GameRoom, Game, PlayerGame
from finance.models import Account, Transaction as FinanceTransaction, WithdrawalRequest as FinanceWithdrawalRequest

BACK_URL = config("BACK_URL")

@sync_to_async
def daily_withdraw_limit(user_id):
    """
    Check if user has reached daily withdrawal limit using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        bool: True if user has reached daily limit, False otherwise
    """
    try:
        user = User.objects.get(telegram_id=user_id)
        
        # Get today's successful withdrawals
        today = datetime.now().date()
        daily_withdrawals = WithdrawalRequest.objects.filter(
            user=user,
            created_at__date=today,
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get payment settings for daily limit
        payment_settings = PaymentSettings.get_solo()
        daily_limit = payment_settings.max_withdrawal_amount
        
        # Return True if user has reached daily limit
        return float(daily_withdrawals) >= daily_limit
    except User.DoesNotExist:
        return True  # Return True (limit reached) on error for safety
    except Exception as e:
        print(f"Error checking daily withdrawal limit: {e}")
        return True  # Return True (limit reached) on error for safety

@sync_to_async
def numnber_of_game_played(user_id):
    """
    Get number of games played by a user using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        int: Number of games played
    """
    try:
        user = User.objects.get(telegram_id=user_id)
        games_played = PlayerGame.objects.filter(user=user).count()
        return games_played
    except User.DoesNotExist:
        return 0
    except Exception as e:
        print(f"Error getting number of games played: {e}")
        return 0

@sync_to_async
def number_of_game_won(user_id):
    """
    Get number of games won by a user using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        int: Number of games won
    """
    try:
        user = User.objects.get(telegram_id=user_id)
        games_won = PlayerGame.objects.filter(user=user, has_bingo=True).count()
        return games_won
    except User.DoesNotExist:
        return 0
    except Exception as e:
        print(f"Error getting number of games won: {e}")
        return 0

# is deposited player
@sync_to_async
def is_deposited_player(user_id):
    """
    Check if a user has made any deposits using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        bool: True if user has made deposits, False otherwise
    """
    try:
        user = User.objects.get(telegram_id=user_id)
        has_deposits = Transaction.objects.filter(
            user=user, 
            type='DEPOSIT',
            status='success'
        ).exists()
        print(f"is deposited for user {user_id}: {has_deposits}")
        return has_deposits
    except User.DoesNotExist:
        print(f"User {user_id} not found")
        return False
    except Exception as e:
        print(f"Error checking if user is deposited: {e}")
        return False
    



@sync_to_async
def get_user_phone(user_id):
    """
    Get user's phone number using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        str: User's phone number or None if not found
    """
    print(f"DEBUG: Getting phone for user_id: {user_id}")
    try:
        user = User.objects.get(telegram_id=user_id)
        phone = user.phone
        print(f"DEBUG: Retrieved phone number: {phone} (type: {type(phone)})")
        return phone
    except User.DoesNotExist:
        print(f"DEBUG: User {user_id} not found")
        return None
    except Exception as e:
        print(f"DEBUG: Error getting phone for user_id: {user_id}, error: {e}")
        return None
    
def verify_receipt(message,paymentMethod,session_id):
    """
    Verify a receipt by reference number
    
    Args:
        message (str): The message to verify
        
    Returns:
        dict: Response from the verification endpoint
    """
    manual_pay_url = config("MANUAL_BASE_URL")
    print("manual payment url")
    callbackurl = BACK_URL +  "/api/v1/wallet/manual/callback/success/"
   
    print("callbackurl = ",callbackurl)
    errorUrl = BACK_URL +  "/api/v1/wallet/manual/callback/error/"
    print("errorUrl = ",errorUrl)
    url = f"{manual_pay_url}receipts/verify/"
    data = {"message": message,"callbackurl":callbackurl,"errorUrl":errorUrl,"paymentMethod":paymentMethod,"session_id":session_id}    
    try:
        response = requests.post(url, json=data)
        print("response = ",response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("error = ",e)
        return {"error": f"Request failed: {str(e)}"}




from game.models import GameRoom
import logging

logger = logging.getLogger(__name__)

@sync_to_async
def get_game_type():
    """
    Get all active game rooms from Django model
    
    Returns:
        dict: Dictionary containing game_types list
    """
    print("++++++++++++++game rooms++++++++++++++")
    try:
        # Get all active game rooms from Django model
        game_rooms = GameRoom.objects.filter(is_active=True)
        print("game_rooms = ",game_rooms)
        game_types = []
        
        for room in game_rooms:
            print("room = ",room)
            game_types.append({
                'bet_amount': str(room.entry_fee),
                'commission': str(room.house_edge_percentage or 0),
                'id': room.id,
                'name': room.name or f"Game Room {room.entry_fee} ETB"
            })
        
        return {'game_types': game_types}
    except Exception as e:
        logger.error(f"Error fetching game rooms from Django model: {e}")
        return None

@sync_to_async
def get_game_type_by_id(room_id):
    """
    Retrieve the type of a game room by its ID.

    Args:
        room_id (int): The primary key of the GameRoom.

    Returns:
        str or None: The room_type if found, else None.
    """
    try:
        room = GameRoom.objects.get(pk=room_id)
        print("room = ",room)
        return room.room_type
    except GameRoom.DoesNotExist:
        return None

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    """Get user by telegram_id"""
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None

@sync_to_async
def get_user_wallet(user):
    """Get user's wallet"""
    try:
        return Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        return None

@sync_to_async
def update_wallet_balance(wallet, new_balance):
    """Update wallet balance"""
    try:
        wallet.balance = new_balance
        wallet.save()
        return True
    except Exception as e:
        print(f"Error updating wallet balance: {e}")
        return False

@sync_to_async
def create_transaction(user, transaction_type, amount, status='pending', description=''):
    """Create a transaction"""
    try:
        transaction = Transaction.objects.create(
            user=user,
            type=transaction_type,
            amount=amount,
            status=status,
            description=description
        )
        return transaction
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return None

@sync_to_async
def get_user_transactions(user, transaction_type=None):
    """Get user transactions"""
    try:
        queryset = Transaction.objects.filter(user=user)
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)
        return list(queryset)
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

@sync_to_async
def create_withdrawal_request(user, amount, phone_number, account_name, bank_name=None, withdrawal_method='bank_transfer'):
    """Create a withdrawal request"""
    try:
        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            phone_number=phone_number,
            account_name=account_name,
            bank_name=bank_name,
            withdrawal_method=withdrawal_method,
            status='pending'
        )
        return withdrawal
    except Exception as e:
        print(f"Error creating withdrawal request: {e}")
        return None

@sync_to_async
def get_user_withdrawal_requests(user, status=None):
    """Get user's withdrawal requests"""
    try:
        from wallet.models import WithdrawalRequest
        queryset = WithdrawalRequest.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        return list(queryset.order_by('-created_at'))
    except Exception as e:
        print(f"Error getting user withdrawal requests: {e}")
        return []


@sync_to_async
def trigger_withdrawal_processing(withdrawal_request_id):
    """Trigger Celery task to process withdrawal request"""
    try:
        from wallet.tasks import process_withdrawal_request
        task = process_withdrawal_request.delay(withdrawal_request_id)
        return task
    except Exception as e:
        print(f"Error triggering withdrawal processing: {e}")
        return None

@sync_to_async
def trigger_withdrawal_validation(user_id, amount, withdrawal_method='bank_transfer'):
    """Trigger Celery task to validate withdrawal amount"""
    try:
        from wallet.tasks import validate_withdrawal_amount
        task = validate_withdrawal_amount.delay(user_id, amount, withdrawal_method)
        return task
    except Exception as e:
        print(f"Error triggering withdrawal validation: {e}")
        return None

@sync_to_async
def trigger_withdrawal_notification(telegram_id, status, amount, withdrawal_id):
    """Trigger Celery task to send withdrawal notification"""
    try:
        from wallet.tasks import send_withdrawal_notification
        task = send_withdrawal_notification.delay(telegram_id, status, amount, withdrawal_id)
        return task
    except Exception as e:
        print(f"Error triggering withdrawal notification: {e}")
        return None

@sync_to_async
def trigger_limit_check(user_id):
    """Trigger Celery task to check withdrawal limits"""
    try:
        from wallet.tasks import check_withdrawal_limits
        task = check_withdrawal_limits.delay(user_id)
        return task
    except Exception as e:
        print(f"Error triggering limit check: {e}")
        return None

@sync_to_async
def get_payment_settings():
    """Get payment settings"""
    try:
        from wallet.models import PaymentSettings
        settings = PaymentSettings.get_solo()
        return {
            'min_withdrawal_amount': settings.min_withdrawal_amount,
            'max_withdrawal_amount': settings.max_withdrawal_amount,
            'min_deposit_amount': settings.min_deposit_amount,
            'withdrawal_fee_percent': settings.withdrawal_fee_percent
        }
    except Exception as e:
        print(f"Error getting payment settings: {e}")
        return {
            'min_withdrawal_amount': 50.0,
            'max_withdrawal_amount': 1000.0,
            'min_deposit_amount': 50.0,
            'withdrawal_fee_percent': 0.0
        }

@sync_to_async
def get_user_wallet_with_referrals(user):
    """Get user's wallet including referral earnings"""
    try:
        wallet = Wallet.objects.get(user=user)
        # Include referral earnings if they meet the threshold
        total_balance = wallet.balance
        if wallet.total_referral_earnings > 500:
            total_balance += wallet.total_referral_earnings
        return {
            'balance': wallet.balance,
            'total_referral_earnings': wallet.total_referral_earnings,
            'total_balance': total_balance,
            'unwithdrawable_bonus': wallet.unwithdrawable_bonus
        }
    except Wallet.DoesNotExist:
        return {
            'balance': 0.0,
            'total_referral_earnings': 0.0,
            'total_balance': 0.0,
            'unwithdrawable_bonus': 0.0
        }
    except Exception as e:
        print(f"Error getting wallet with referrals: {e}")
        return {
            'balance': 0.0,
            'total_referral_earnings': 0.0,
            'total_balance': 0.0,
            'unwithdrawable_bonus': 0.0
        }


@sync_to_async
def get_user_game_statistics(user):
    """Get user game statistics using Django ORM"""
    try:
        # Get games played this week
        week_ago = datetime.now() - timedelta(days=7)
        games_played_this_week = PlayerGame.objects.filter(
            user=user,
            joined_at__gte=week_ago
        ).count()
        
        # Get total games played
        total_games_played = PlayerGame.objects.filter(user=user).count()
        
        # Get total games won
        total_games_won = PlayerGame.objects.filter(
            user=user,
            is_winner=True
        ).count()
        
        return {
            'games_played_this_week': games_played_this_week,
            'total_games_played': total_games_played,
            'total_games_won': total_games_won
        }
    except Exception as e:
        print(f"Error getting user game statistics: {e}")
        return {
            'games_played_this_week': 0,
            'total_games_played': 0,
            'total_games_won': 0
        }


@sync_to_async
def notify_referrer_bonus(referrer_telegram_id, referred_user_name):
    """Notify referrer about bonus received"""
    try:
        # This would typically send a notification to the referrer
        # For now, we'll just log it
        print(f"🎉 Referral Bonus: User {referrer_telegram_id} received 5 ETB for referring {referred_user_name}")
        return True
    except Exception as e:
        print(f"Error notifying referrer: {e}")
        return False
