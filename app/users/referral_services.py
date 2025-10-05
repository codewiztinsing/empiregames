import logging
from django.db import transaction, models
from django.utils import timezone
from datetime import date, timedelta
from .models import User, ReferralBonus, WithdrawalRequest
from wallet.models import Wallet

logger = logging.getLogger(__name__)


class ReferralService:
    """Service class for handling referral system operations"""
    
    @staticmethod
    def set_referrer(user, referral_code):
        """Set referrer for a user using referral code"""
        if user.sponsor_changed:
            return False, "You can only change sponsor once"
        
        try:
            referrer = User.objects.get(referral_code=referral_code)
            if referrer == user:
                return False, "Cannot refer yourself"
            
            user.referred_by = referrer
            user.is_agent = False  # User is no longer agent under Aker Bingo
            user.sponsor_changed = True
            user.save()
            
            # Process sponsor change bonus if this is a sponsor change
            if user.referred_by is not None:  # If user already had a referrer before
                ReferralService.process_sponsor_change_bonus(user)
            
            return True, "Sponsor set successfully"
        except User.DoesNotExist:
            return False, "Invalid referral code"
    
    @staticmethod
    def process_win_bonus(winner, win_amount, game_id):
        """Process referral bonuses when a user wins"""
        
        print(f"Winner: in referral services {winner.referred_by}")
        # First generation (4% bonus)
        if winner.referred_by:
            first_gen_bonus = ReferralService._create_bonus(
                winner.referred_by, winner, win_amount, game_id, 
                'first_generation', float('0.04'), 1
            )
            
            # Second generation (1% bonus)
            if winner.referred_by.referred_by:
                second_gen_bonus = ReferralService._create_bonus(
                    winner.referred_by.referred_by, winner, win_amount, game_id,
                    'second_generation', float('0.01'), 2
                )
                
               
        
        return True
    
    @staticmethod
    def process_signup_bonus(user):
        """Process 10 birr signup bonus for new customers"""
        if user.signup_bonus_claimed:
            return False, "Signup bonus already claimed"
        
        # Create and immediately approve signup bonus
        bonus = ReferralService._create_bonus(
            user, user, float('10.00'), 'signup', 
            'signup', float('1.00'), 0
        )
        
        # Immediately approve the bonus
        bonus.status = 'approved'
        bonus.save()
        
        # Add to user's total earnings and wallet
        user.total_referral_earnings += float(bonus.bonus_amount)
        user.signup_bonus_claimed = True
        user.save()
        
        # Add to wallet
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance += float(bonus.bonus_amount)
        wallet.save()
        
        return True, "Signup bonus processed and added to wallet"
    
    @staticmethod
    def process_sponsor_change_bonus(user):
        """Process 10 birr bonus for sponsor change (one-time only)"""
        if user.sponsor_change_bonus_claimed:
            return False, "Sponsor change bonus already claimed"
        
        # Create and immediately approve sponsor change bonus
        bonus = ReferralService._create_bonus(
            user, user, float('10.00'), 'sponsor_change', 
            'sponsor_change', float('1.00'), 0
        )
        
        # Immediately approve the bonus
        bonus.status = 'approved'
        bonus.save()
        
        # Add to user's total earnings and wallet
        user.total_referral_earnings += float(bonus.bonus_amount)
        user.sponsor_change_bonus_claimed = True
        user.save()
        
        # Add to wallet
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance += float(bonus.bonus_amount)
        wallet.save()
        
        return True, "Sponsor change bonus processed and added to wallet"
    
    @staticmethod
    def process_tuesday_bonus_payments():
        """Process bonus payments every Tuesday"""
        from datetime import datetime
        today = timezone.now().date()
        
        # Check if today is Tuesday (weekday() returns 1 for Tuesday)
        if today.weekday() != 1:
            return False, "Today is not Tuesday"
        
        # Get all pending bonuses
        pending_bonuses = ReferralBonus.objects.filter(status='pending')
        approved_count = 0
        
        for bonus in pending_bonuses:
            try:
                # Check if user qualifies for withdrawal
                can_withdraw, _ = ReferralService.can_withdraw(bonus.referrer)
                if can_withdraw:
                    # Approve the bonus
                    success, message = ReferralService.approve_bonus(bonus.id, None)
                    if success:
                        approved_count += 1
                else:
                    # Move to unwithdrawable bonus
                    ReferralService._move_to_unwithdrawable_bonus(bonus)
            except Exception as e:
                logger.error(f"Error processing bonus {bonus.id}: {e}")
        
        return True, f"Processed {approved_count} bonuses on Tuesday"
    
    @staticmethod
    def _move_to_unwithdrawable_bonus(bonus):
        """Move bonus to unwithdrawable balance"""
        bonus.status = 'approved'
        bonus.save()
        
        # Add to unwithdrawable bonus
        wallet, created = Wallet.objects.get_or_create(user=bonus.referrer)
        wallet.unwithdrawable_bonus += float(bonus.bonus_amount)
        wallet.save()
        
        # Add to user's total earnings
        bonus.referrer.unwithdrawable_bonus += float(bonus.bonus_amount)
        bonus.referrer.save()
    
    @staticmethod
    def get_or_create_default_sponsor():
        """Get or create the default sponsor (Akerbingo)"""
        try:
            default_sponsor = User.objects.get(username='Akerbingo')
        except User.DoesNotExist:
            # Create default sponsor if it doesn't exist
            default_sponsor = User.objects.create(
                username='Akerbingo',
                phone='0000000000',
                telegram_id='0',
                is_agent=True,
                is_active=True
            )
        return default_sponsor
    
    @staticmethod
    def use_unwithdrawable_bonus_for_play(user, amount):
        """Use unwithdrawable bonus for playing games"""
        if user.unwithdrawable_bonus < float(amount):
            return False, "Insufficient unwithdrawable bonus"
        
        # Deduct from unwithdrawable bonus
        user.unwithdrawable_bonus -= float(amount)
        user.save()
        
        # Add to regular wallet balance for playing
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance += float(amount)
        wallet.unwithdrawable_bonus -= float(amount)
        wallet.save()
        
        return True, "Unwithdrawable bonus used for playing"
    
    @staticmethod
    def _create_bonus(referrer, winner, win_amount, game_id, bonus_type, percentage, generation_level):
        """Create a referral bonus record"""
        bonus_amount = float(win_amount) * float(percentage)
        
        # Create the ReferralBonus object
        bonus = ReferralBonus.objects.create(
            referrer=referrer,
            winner=winner,
            game_id=game_id,
            win_amount=float(win_amount),
            bonus_type=bonus_type,
            bonus_amount=bonus_amount,
            generation_level=generation_level,
            status='pending'
        )
        
        return bonus
    
    @staticmethod
    def approve_bonus(bonus_id, admin_user):
        """Approve a referral bonus and add to user's wallet"""
        try:
            bonus = ReferralBonus.objects.get(id=bonus_id, status='pending')
            
            with transaction.atomic():
                # Update bonus status
                bonus.status = 'approved'
                bonus.save()
                
                # Add to user's total earnings
                bonus.referrer.total_referral_earnings += float(bonus.bonus_amount)
                bonus.referrer.save()
                
                # Add to wallet
                wallet, created = Wallet.objects.get_or_create(user=bonus.referrer)
                wallet.balance += bonus.bonus_amount
                wallet.save()
                
            return True, "Bonus approved and added to wallet"
        except ReferralBonus.DoesNotExist:
            return False, "Bonus not found"
    
    @staticmethod
    def update_game_stats(user):
        """Update user's game statistics"""
        today = timezone.now().date()
        
        # Reset daily count if new day
        if user.last_game_date != today:
            user.games_played_today = 0
            user.last_game_date = today
        
        # Reset weekly count if new week
        week_start = today - timedelta(days=today.weekday())
        if not user.last_week_reset or user.last_week_reset < week_start:
            user.games_played_this_week = 0
            user.last_week_reset = week_start
        
        # Update counts
        user.games_played_today += 1
        user.games_played_this_week += 1
        user.total_games_played += 1
        user.save()
    
    @staticmethod
    def can_withdraw(user):
        """Check if user can withdraw referral earnings"""
        # Check minimum amount
        if user.total_referral_earnings < float('500.00'):
            return False, "Minimum withdrawal amount is 500 birr"
        
        # Check qualification: 3 games per day OR 27 games per week
        if user.games_played_today < 3 and user.games_played_this_week < 27:
            return False, "Must play at least 3 games today OR 27 games this week"
        
        return True, "Eligible for withdrawal"
    
    @staticmethod
    def create_withdrawal_request(user, amount):
        """Create a withdrawal request"""
        can_withdraw, message = ReferralService.can_withdraw(user)
        if not can_withdraw:
            return False, message
        
        if amount < float('500.00'):
            return False, "Minimum withdrawal amount is 500 birr"
        
        if amount > user.total_referral_earnings:
            return False, "Insufficient referral earnings"
        
        # Check for pending requests
        pending_requests = WithdrawalRequest.objects.filter(
            user=user, 
            status__in=['pending', 'approved']
        )
        if pending_requests.exists():
            return False, "You have a pending withdrawal request"
        
        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            status='pending'
        )
        
        return True, "Withdrawal request created successfully"
    
    @staticmethod
    def get_referral_stats(user):
        """Get referral statistics for a user"""
        first_gen_referrals = user.referrals.all()
        second_gen_referrals = User.objects.filter(referred_by__in=first_gen_referrals)
        
        total_referrals = first_gen_referrals.count()
        total_second_gen = second_gen_referrals.count()
        
        total_earnings = user.total_referral_earnings
        pending_bonuses = ReferralBonus.objects.filter(
            referrer=user, 
            status='pending'
        ).aggregate(total=models.Sum('bonus_amount'))['total'] or float('0.00')
        
        return {
            'total_referrals': total_referrals,
            'total_second_gen': total_second_gen,
            'total_earnings': total_earnings,
            'pending_bonuses': pending_bonuses,
            'games_played_today': user.games_played_today,
            'games_played_this_week': user.games_played_this_week,
            'can_withdraw': ReferralService.can_withdraw(user)[0]
        }
