import logging
from celery import shared_task
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import WithdrawalRequest, Wallet, Transaction, PaymentSettings
from users.models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_withdrawal_request(self, withdrawal_request_id):
    """
    Process a withdrawal request asynchronously.
    
    Args:
        withdrawal_request_id (int): ID of the WithdrawalRequest to process
        
    Returns:
        dict: Result of the processing operation
    """
    logger.info(f"=== PROCESS_WITHDRAWAL_REQUEST TASK STARTED ===")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Withdrawal Request ID: {withdrawal_request_id}")
    
    try:
        # Get the withdrawal request
        withdrawal_request = get_object_or_404(WithdrawalRequest, id=withdrawal_request_id)
        logger.info(f"Processing withdrawal request: {withdrawal_request}")
        
        # Check if already processed
        if withdrawal_request.status in ['success', 'failed', 'cancelled']:
            logger.info(f"Withdrawal request {withdrawal_request_id} already processed with status: {withdrawal_request.status}")
            return {
                'success': False,
                'message': f'Withdrawal request already processed with status: {withdrawal_request.status}',
                'withdrawal_id': withdrawal_request_id
            }
        
        # Update status to processing
        withdrawal_request.status = 'processing'
        withdrawal_request.save()
        
        # Get user and wallet
        user = withdrawal_request.user
        wallet = get_object_or_404(Wallet, user=user)
        
        logger.info(f"User: {user.username}, Current balance: {wallet.balance}")
        
        # Validate withdrawal amount
        if wallet.balance < withdrawal_request.amount:
            withdrawal_request.status = 'failed'
            withdrawal_request.failure_reason = 'Insufficient balance'
            withdrawal_request.save()
            
            logger.warning(f"Insufficient balance for withdrawal: {wallet.balance} < {withdrawal_request.amount}")
            return {
                'success': False,
                'message': 'Insufficient balance',
                'withdrawal_id': withdrawal_request_id
            }
        
        # Process the withdrawal (simulate external payment processing)
        # In a real implementation, this would integrate with payment gateways
        logger.info(f"Processing withdrawal of {withdrawal_request.amount} ETB to {withdrawal_request.phone_number}")
        
        # Simulate processing delay
        import time
        time.sleep(2)  # Simulate external API call
        
        # Deduct amount from wallet
        with transaction.atomic():
            wallet.balance -= withdrawal_request.amount
            wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=user,
                amount=withdrawal_request.amount,
                type='WITHDRAW',
                status='success',
                reference=f'WITHDRAW_{withdrawal_request_id}'
            )
            
            # Update withdrawal request
            withdrawal_request.status = 'success'
            withdrawal_request.processed_at = timezone.now()
            withdrawal_request.save()
        
        logger.info(f"Withdrawal processed successfully. New balance: {wallet.balance}")
        
        # Send notification to user
        send_withdrawal_notification.delay(
            user.telegram_id,
            'success',
            withdrawal_request.amount,
            withdrawal_request_id
        )
        
        logger.info(f"=== PROCESS_WITHDRAWAL_REQUEST TASK COMPLETED ===")
        return {
            'success': True,
            'message': 'Withdrawal processed successfully',
            'withdrawal_id': withdrawal_request_id,
            'new_balance': wallet.balance
        }
        
    except Exception as e:
        logger.error(f"Error processing withdrawal request {withdrawal_request_id}: {str(e)}")
        
        # Update withdrawal request status to failed
        try:
            withdrawal_request = WithdrawalRequest.objects.get(id=withdrawal_request_id)
            withdrawal_request.status = 'failed'
            withdrawal_request.failure_reason = str(e)
            withdrawal_request.save()
        except:
            pass
        
        # Retry the task if it's not the final retry
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying withdrawal processing (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60)
        else:
            logger.error(f"Max retries reached for withdrawal request {withdrawal_request_id}")
            return {
                'success': False,
                'message': f'Failed to process withdrawal after {self.max_retries} retries: {str(e)}',
                'withdrawal_id': withdrawal_request_id
            }


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def validate_withdrawal_amount(self, user_id, amount, withdrawal_method='bank_transfer'):
    """
    Validate withdrawal amount against user's balance and limits.
    
    Args:
        user_id (int): User's telegram_id
        amount (float): Amount to withdraw
        withdrawal_method (str): Method of withdrawal
        
    Returns:
        dict: Validation result
    """
    logger.info(f"=== VALIDATE_WITHDRAWAL_AMOUNT TASK STARTED ===")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"User ID: {user_id}, Amount: {amount}, Method: {withdrawal_method}")
    
    try:
        # Get user and wallet
        user = get_object_or_404(User, telegram_id=str(user_id))
        wallet = get_object_or_404(Wallet, user=user)
        
        # Get payment settings
        payment_settings = PaymentSettings.get_solo()
        
        # Validate minimum amount
        if amount < payment_settings.min_withdrawal_amount:
            return {
                'valid': False,
                'reason': f'Amount must be at least {payment_settings.min_withdrawal_amount} ETB',
                'min_amount': payment_settings.min_withdrawal_amount
            }
        
        # Validate maximum amount
        if payment_settings.max_withdrawal_amount > 0 and amount > payment_settings.max_withdrawal_amount:
            return {
                'valid': False,
                'reason': f'Amount must not exceed {payment_settings.max_withdrawal_amount} ETB',
                'max_amount': payment_settings.max_withdrawal_amount
            }
        
        # Validate balance
        if wallet.balance < amount:
            return {
                'valid': False,
                'reason': 'Insufficient balance',
                'current_balance': wallet.balance,
                'requested_amount': amount
            }
        
        # Check minimum balance requirement (leave at least 20 ETB)
        min_balance_required = 20.0
        if wallet.balance - amount < min_balance_required:
            return {
                'valid': False,
                'reason': f'Must leave at least {min_balance_required} ETB in wallet',
                'current_balance': wallet.balance,
                'min_balance_required': min_balance_required
            }
        
        logger.info(f"Withdrawal validation successful for user {user.username}")
        
        return {
            'valid': True,
            'current_balance': wallet.balance,
            'amount': amount,
            'remaining_balance': wallet.balance - amount
        }
        
    except Exception as e:
        logger.error(f"Error validating withdrawal amount: {str(e)}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying validation (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30)
        else:
            return {
                'valid': False,
                'reason': f'Validation failed: {str(e)}'
            }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_withdrawal_notification(self, telegram_id, status, amount, withdrawal_id):
    """
    Send withdrawal notification to user via Telegram.
    
    Args:
        telegram_id (int): User's Telegram ID
        status (str): Withdrawal status ('success', 'failed', 'processing')
        amount (float): Withdrawal amount
        withdrawal_id (int): Withdrawal request ID
        
    Returns:
        dict: Notification result
    """
    logger.info(f"=== SEND_WITHDRAWAL_NOTIFICATION TASK STARTED ===")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Telegram ID: {telegram_id}, Status: {status}, Amount: {amount}")
    
    try:
        from decouple import config
        import requests
        
        bot_token = config('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not configured")
            return {'success': False, 'message': 'Bot token not configured'}
        
        # Prepare notification message
        if status == 'success':
            message = f"✅ Withdrawal Successful!\n\n"
            message += f"Amount: {amount} ETB\n"
            message += f"Status: Processed\n"
            message += f"Reference: WITHDRAW_{withdrawal_id}\n\n"
            message += f"Your withdrawal has been processed successfully."
        elif status == 'failed':
            message = f"❌ Withdrawal Failed\n\n"
            message += f"Amount: {amount} ETB\n"
            message += f"Status: Failed\n"
            message += f"Reference: WITHDRAW_{withdrawal_id}\n\n"
            message += f"Your withdrawal request could not be processed. Please contact support."
        elif status == 'processing':
            message = f"⏳ Withdrawal Processing\n\n"
            message += f"Amount: {amount} ETB\n"
            message += f"Status: Processing\n"
            message += f"Reference: WITHDRAW_{withdrawal_id}\n\n"
            message += f"Your withdrawal is being processed. You will be notified when completed."
        else:
            message = f"📋 Withdrawal Update\n\n"
            message += f"Amount: {amount} ETB\n"
            message += f"Status: {status}\n"
            message += f"Reference: WITHDRAW_{withdrawal_id}"
        
        # Send message via Telegram API
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Withdrawal notification sent successfully to user {telegram_id}")
            return {
                'success': True,
                'message': 'Notification sent successfully',
                'telegram_id': telegram_id
            }
        else:
            logger.error(f"Failed to send notification: {response.status_code} - {response.text}")
            return {
                'success': False,
                'message': f'Failed to send notification: {response.status_code}',
                'telegram_id': telegram_id
            }
            
    except Exception as e:
        logger.error(f"Error sending withdrawal notification: {str(e)}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying notification (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60)
        else:
            return {
                'success': False,
                'message': f'Failed to send notification after {self.max_retries} retries: {str(e)}',
                'telegram_id': telegram_id
            }


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def check_withdrawal_limits(self, user_id):
    """
    Check user's withdrawal limits and restrictions.
    
    Args:
        user_id (int): User's telegram_id
        
    Returns:
        dict: Limit check result
    """
    logger.info(f"=== CHECK_WITHDRAWAL_LIMITS TASK STARTED ===")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"User ID: {user_id}")
    
    try:
        from utils.helpers import daily_withdraw_limit, is_deposited_player, numnber_of_game_played, number_of_game_won
        
        # Check daily withdrawal limit
        daily_limit = daily_withdraw_limit(user_id)
        
        # Check if user has deposited
        is_deposited = is_deposited_player(user_id)
        
        # Check games played and won
        games_played = numnber_of_game_played(user_id)
        games_won = number_of_game_won(user_id)
        
        # Check if user meets minimum requirements
        meets_requirements = {
            'has_deposited': is_deposited,
            'games_played_sufficient': games_played >= 5,
            'games_won_sufficient': games_won >= 2,
            'daily_limit_ok': daily_limit <= 3
        }
        
        can_withdraw = all(meets_requirements.values())
        
        logger.info(f"Withdrawal limits check for user {user_id}: {meets_requirements}")
        
        return {
            'can_withdraw': can_withdraw,
            'requirements': meets_requirements,
            'daily_limit': daily_limit,
            'games_played': games_played,
            'games_won': games_won,
            'is_deposited': is_deposited
        }
        
    except Exception as e:
        logger.error(f"Error checking withdrawal limits: {str(e)}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying limit check (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30)
        else:
            return {
                'can_withdraw': False,
                'error': f'Failed to check limits: {str(e)}'
            }
