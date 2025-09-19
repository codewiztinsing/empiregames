from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from datetime import date, timedelta
from .models import User, ReferralBonus, WithdrawalRequest
from wallet.models import Wallet


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
            return True, "Sponsor set successfully"
        except User.DoesNotExist:
            return False, "Invalid referral code"
    
    @staticmethod
    def process_win_bonus(winner, win_amount, game_id):
        """Process referral bonuses when a user wins"""
        bonuses_created = []
        
        # First generation (4% bonus)
        if winner.referred_by:
            first_gen_bonus = ReferralService._create_bonus(
                winner.referred_by, winner, win_amount, game_id, 
                'first_generation', Decimal('0.04'), 1
            )
            bonuses_created.append(first_gen_bonus)
            
            # Second generation (1% bonus)
            if winner.referred_by.referred_by:
                second_gen_bonus = ReferralService._create_bonus(
                    winner.referred_by.referred_by, winner, win_amount, game_id,
                    'second_generation', Decimal('0.01'), 2
                )
                bonuses_created.append(second_gen_bonus)
        
        # Inhouse bonus (3% for Aker Bingo agents)
        aker_agents = User.objects.filter(is_agent=True)
        for agent in aker_agents:
            inhouse_bonus = ReferralService._create_bonus(
                agent, winner, win_amount, game_id,
                'inhouse', Decimal('0.03'), 0
            )
            bonuses_created.append(inhouse_bonus)
        
        return bonuses_created
    
    @staticmethod
    def _create_bonus(referrer, winner, win_amount, game_id, bonus_type, percentage, generation_level):
        """Create a referral bonus record"""
        bonus_amount = win_amount * percentage
        
        bonus = ReferralBonus.objects.create(
            referrer=referrer,
            winner=winner,
            game_id=game_id,
            win_amount=win_amount,
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
                bonus.referrer.total_referral_earnings += bonus.bonus_amount
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
        if user.total_referral_earnings < Decimal('500.00'):
            return False, "Minimum withdrawal amount is 500 birr"
        
        # Check daily games requirement (3 games per day)
        if user.games_played_today < 3:
            return False, "Must play at least 3 games today"
        
        # Check weekly games requirement (27 games per week)
        if user.games_played_this_week < 27:
            return False, "Must play at least 27 games this week"
        
        return True, "Eligible for withdrawal"
    
    @staticmethod
    def create_withdrawal_request(user, amount):
        """Create a withdrawal request"""
        can_withdraw, message = ReferralService.can_withdraw(user)
        if not can_withdraw:
            return False, message
        
        if amount < Decimal('500.00'):
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
        ).aggregate(total=models.Sum('bonus_amount'))['total'] or Decimal('0.00')
        
        return {
            'total_referrals': total_referrals,
            'total_second_gen': total_second_gen,
            'total_earnings': total_earnings,
            'pending_bonuses': pending_bonuses,
            'games_played_today': user.games_played_today,
            'games_played_this_week': user.games_played_this_week,
            'can_withdraw': ReferralService.can_withdraw(user)[0]
        }
