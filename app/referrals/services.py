from django.db import transaction, models
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from .models import ReferralBonus, ReferralWithdrawal, UserGameStats, ReferralSettings
from users.models import User
from wallet.models import Transaction

class ReferralService:
    """Service class for handling referral system logic"""
    
    @staticmethod
    def calculate_referral_bonuses(winner_user, win_amount, game_id=None):
        """
        Calculate and distribute referral bonuses when a user wins
        A -> B -> C -> D
        If B wins 1000 birr:
        - A gets 4% (40 birr)
        - If C wins 1000 birr: B gets 4% (40 birr), A gets 1% (10 birr)
        """
        settings = ReferralSettings.get_settings()
        
        # Get sponsor (first generation)
        sponsor = winner_user.sponsor
        if not sponsor:
            return
        
        # First generation bonus (4%)
        first_gen_bonus = Decimal(str(win_amount)) * (settings.first_generation_bonus / 100)
        ReferralBonus.objects.create(
            user=sponsor,
            from_user=winner_user,
            generation=1,
            win_amount=win_amount,
            bonus_percentage=settings.first_generation_bonus,
            bonus_amount=first_gen_bonus,
            game_id=game_id,
            status='approved'
        )
        
        # Add bonus to sponsor's wallet
        ReferralService._add_bonus_to_wallet(sponsor, first_gen_bonus)
        
        # Second generation bonus (1%)
        grand_sponsor = sponsor.sponsor
        if grand_sponsor:
            second_gen_bonus = Decimal(str(win_amount)) * (settings.second_generation_bonus / 100)
            ReferralBonus.objects.create(
                user=grand_sponsor,
                from_user=winner_user,
                generation=2,
                win_amount=win_amount,
                bonus_percentage=settings.second_generation_bonus,
                bonus_amount=second_gen_bonus,
                game_id=game_id,
                status='approved'
            )
            
            # Add bonus to grand sponsor's wallet
            ReferralService._add_bonus_to_wallet(grand_sponsor, second_gen_bonus)
    
    @staticmethod
    def _add_bonus_to_wallet(user, amount):
        """Add referral bonus to user's wallet"""
        from wallet.models import Wallet
        
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance += float(amount)
        wallet.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=user,
            amount=amount,
            type='REFERRAL_BONUS',
            status='success',
            reference=f'REF_BONUS_{timezone.now().strftime("%Y%m%d%H%M%S")}'
        )
    
    @staticmethod
    def update_user_game_stats(user):
        """Update user's game statistics"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        stats, created = UserGameStats.objects.get_or_create(user=user)
        
        if stats.last_game_date != today:
            # New day, reset daily count
            stats.games_played_today = 1
            stats.last_game_date = today
        else:
            stats.games_played_today += 1
        
        if stats.last_week_reset != week_start:
            # New week, reset weekly count
            stats.games_played_this_week = 1
            stats.last_week_reset = week_start
        else:
            stats.games_played_this_week += 1
        
        stats.total_games_played += 1
        stats.save()
    
    @staticmethod
    def can_withdraw_referral_bonus(user):
        """Check if user can withdraw referral bonus based on game requirements"""
        settings = ReferralSettings.get_settings()
        
        try:
            stats = user.game_stats
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            # Check if it's a new week (reset weekly count)
            if stats.last_week_reset != week_start:
                return False
            
            # Check daily requirement (3 games per day)
            if stats.games_played_today < settings.daily_games_required:
                return False
            
            # Check weekly requirement (27 games per week)
            if stats.games_played_this_week < settings.weekly_games_required:
                return False
            
            return True
        except UserGameStats.DoesNotExist:
            return False
    
    @staticmethod
    def get_available_referral_balance(user):
        """Get user's available referral bonus balance"""
        total_bonuses = ReferralBonus.objects.filter(
            user=user, 
            status='approved'
        ).aggregate(total=models.Sum('bonus_amount'))['total'] or Decimal('0')
        
        total_withdrawn = ReferralWithdrawal.objects.filter(
            user=user,
            status__in=['approved', 'paid']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        return total_bonuses - total_withdrawn
    
    @staticmethod
    def request_withdrawal(user, amount):
        """Request withdrawal of referral bonus"""
        settings = ReferralSettings.get_settings()
        
        # Check minimum withdrawal amount
        if amount < settings.minimum_withdrawal:
            return False, f"Minimum withdrawal amount is {settings.minimum_withdrawal} birr"
        
        # Check if user can withdraw
        if not ReferralService.can_withdraw_referral_bonus(user):
            return False, "You must play 3 games per day and 27 games per week to withdraw"
        
        # Check available balance
        available_balance = ReferralService.get_available_referral_balance(user)
        if amount > available_balance:
            return False, f"Insufficient balance. Available: {available_balance} birr"
        
        # Create withdrawal request
        withdrawal = ReferralWithdrawal.objects.create(
            user=user,
            amount=amount,
            status='pending'
        )
        
        return True, withdrawal
    
    @staticmethod
    def get_referral_tree(user, max_depth=2):
        """Get user's referral tree up to 2 generations"""
        referrals = []
        
        # First generation - get users who have this user as sponsor
        first_gen = User.objects.filter(sponsor=user)
        for ref in first_gen:
            referrals.append({
                'user': ref,
                'generation': 1,
                'referrals': []
            })
            
            # Second generation - get users who have first gen user as sponsor
            second_gen = User.objects.filter(sponsor=ref)
            for ref2 in second_gen:
                referrals[-1]['referrals'].append({
                    'user': ref2,
                    'generation': 2,
                    'referrals': []
                })
        
        return referrals

class ReferralSignals:
    """Handle referral-related signals"""
    
    @staticmethod
    def handle_user_registration(sender, instance, created, **kwargs):
        """Handle new user registration and set as agent if no sponsor"""
        if created and not instance.sponsor:
            instance.is_agent = True
            instance.save()
    
    @staticmethod
    def handle_game_win(sender, instance, created, **kwargs):
        """Handle game win and calculate referral bonuses"""
        if created and instance.type == 'WIN' and instance.status == 'success':
            ReferralService.calculate_referral_bonuses(
                instance.user, 
                instance.amount,
                getattr(instance, 'game_id', None)
            )
    
    @staticmethod
    def handle_game_play(sender, instance, created, **kwargs):
        """Handle game play and update statistics"""
        if created and instance.type == 'BET':
            ReferralService.update_user_game_stats(instance.user)
