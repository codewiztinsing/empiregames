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
from wallet.models import Wallet, Transaction, WithdrawalRequest
from game.models import GameRoom, Game, PlayerGame
from finance.models import Account, Transaction as FinanceTransaction, WithdrawalRequest as FinanceWithdrawalRequest

BACK_URL = config("BACK_URL")

@sync_to_async
def daily_withdraw_limit(user_id):
    """
    Get daily withdrawal limit for a user using Django ORM
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        float: Daily withdrawal limit amount
    """
    try:
        user = User.objects.get(telegram_id=user_id)
        wallet = Wallet.objects.filter(user=user).first()
        
        if wallet:
            # Get today's withdrawals
            today = datetime.now().date()
            daily_withdrawals = WithdrawalRequest.objects.filter(
                user=user,
                created_at__date=today,
                status='success'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Return remaining limit (assuming 1000 ETB daily limit)
            daily_limit = 1000.0
            return max(0, daily_limit - float(daily_withdrawals))
        else:
            return 0
    except User.DoesNotExist:
        return 0
    except Exception as e:
        print(f"Error getting daily withdraw limit: {e}")
        return 0

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
def create_withdrawal_request(user, amount, phone_number, account_name):
    """Create a withdrawal request"""
    try:
        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            phone_number=phone_number,
            account_name=account_name,
            status='pending'
        )
        return withdrawal
    except Exception as e:
        print(f"Error creating withdrawal request: {e}")
        return None

@sync_to_async
def get_user_withdrawal_requests(user):
    """Get user's withdrawal requests"""
    try:
        return list(WithdrawalRequest.objects.filter(user=user))
    except Exception as e:
        print(f"Error getting withdrawal requests: {e}")
        return []
