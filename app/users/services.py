from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User
from game.models import PlayerGame, Game
from wallet.models import Transaction, Wallet, WithdrawalRequest


class UserStatsService:
    """
    Service class to calculate comprehensive user statistics
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_gaming_stats(self):
        """Get comprehensive gaming statistics"""
        # Total games played
        total_games = PlayerGame.objects.filter(user=self.user).count()
        
        # Games won (user was the winner of completed games)
        games_won = Game.objects.filter(winner=self.user, status='completed').count()
        
        # Games where user got bingo
        bingo_games = PlayerGame.objects.filter(user=self.user, has_bingo=True).count()
        
        # Win rate
        win_rate = (games_won / total_games * 100) if total_games > 0 else 0
        
        # Recent games (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_games = PlayerGame.objects.filter(
            user=self.user, 
            game__created_at__gte=thirty_days_ago
        ).count()
        
        return {
            'total_games_played': total_games,
            'games_won': games_won,
            'bingo_games': bingo_games,
            'win_rate': round(win_rate, 2),
            'recent_games': recent_games,
        }
    
    def get_financial_stats(self):
        """Get comprehensive financial statistics"""
        # Get wallet balance
        try:
            wallet = Wallet.objects.get(user=self.user)
            current_balance = wallet.balance
        except Wallet.DoesNotExist:
            current_balance = 0
        
        # Total deposits
        total_deposits = Transaction.objects.filter(
            user=self.user, 
            type='DEPOSIT', 
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Total withdrawals
        total_withdrawals = Transaction.objects.filter(
            user=self.user, 
            type='WITHDRAW', 
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Total bets placed
        total_bets = Transaction.objects.filter(
            user=self.user, 
            type='BET'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Total winnings
        total_winnings = Transaction.objects.filter(
            user=self.user, 
            type='WIN', 
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Net profit/loss (winnings - bets)
        net_result = total_winnings - total_bets
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_deposits = Transaction.objects.filter(
            user=self.user,
            type='DEPOSIT',
            status='success',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        recent_withdrawals = Transaction.objects.filter(
            user=self.user,
            type='WITHDRAW',
            status='success',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        recent_bets = Transaction.objects.filter(
            user=self.user,
            type='BET',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        recent_winnings = Transaction.objects.filter(
            user=self.user,
            type='WIN',
            status='success',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return {
            'current_balance': current_balance,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_bets': total_bets,
            'total_winnings': total_winnings,
            'net_result': net_result,
            'recent_deposits': recent_deposits,
            'recent_withdrawals': recent_withdrawals,
            'recent_bets': recent_bets,
            'recent_winnings': recent_winnings,
        }
    
    def get_transaction_stats(self):
        """Get transaction statistics and history"""
        # Total transactions
        total_transactions = Transaction.objects.filter(user=self.user).count()
        
        # Transaction breakdown by type
        deposit_count = Transaction.objects.filter(user=self.user, type='DEPOSIT').count()
        withdrawal_count = Transaction.objects.filter(user=self.user, type='WITHDRAW').count()
        bet_count = Transaction.objects.filter(user=self.user, type='BET').count()
        win_count = Transaction.objects.filter(user=self.user, type='WIN').count()
        
        # Pending transactions
        pending_deposits = Transaction.objects.filter(
            user=self.user, 
            type='DEPOSIT', 
            status='pending'
        ).count()
        
        pending_withdrawals = Transaction.objects.filter(
            user=self.user, 
            type='WITHDRAW', 
            status='pending'
        ).count()
        
        # Failed transactions
        failed_transactions = Transaction.objects.filter(
            user=self.user, 
            status='failed'
        ).count()
        
        # Recent transactions (last 10)
        recent_transactions = Transaction.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10]
        
        return {
            'total_transactions': total_transactions,
            'deposit_count': deposit_count,
            'withdrawal_count': withdrawal_count,
            'bet_count': bet_count,
            'win_count': win_count,
            'pending_deposits': pending_deposits,
            'pending_withdrawals': pending_withdrawals,
            'failed_transactions': failed_transactions,
            'recent_transactions': recent_transactions,
        }
    
    def get_withdrawal_requests(self):
        """Get withdrawal request statistics"""
        # Total withdrawal requests
        total_requests = WithdrawalRequest.objects.filter(user=self.user).count()
        
        # Pending requests
        pending_requests = WithdrawalRequest.objects.filter(
            user=self.user, 
            status='pending'
        ).count()
        
        # Successful withdrawals
        successful_requests = WithdrawalRequest.objects.filter(
            user=self.user, 
            status='success'
        ).count()
        
        # Failed withdrawals
        failed_requests = WithdrawalRequest.objects.filter(
            user=self.user, 
            status='failed'
        ).count()
        
        # Recent requests (last 5)
        recent_requests = WithdrawalRequest.objects.filter(
            user=self.user
        ).order_by('-created_at')[:5]
        
        return {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'recent_requests': recent_requests,
        }
    
    def get_referral_stats(self):
        """Get referral statistics"""
        # Total referrals made
        total_referrals = self.user.referrals_made.count()
        
        # Referrals with bonuses paid
        paid_referrals = self.user.referrals_made.filter(bonus_paid=True).count()
        
        # Total bonus earned from referrals
        total_referral_bonus = self.user.referrals_made.filter(
            bonus_paid=True
        ).aggregate(total=Sum('bonus_amount'))['total'] or 0
        
        # Referral code
        referral_code = self.user.referral_code
        
        return {
            'total_referrals': total_referrals,
            'paid_referrals': paid_referrals,
            'total_referral_bonus': total_referral_bonus,
            'referral_code': referral_code,
        }
    
    def get_activity_stats(self):
        """Get user activity statistics"""
        # Account age
        account_age_days = (timezone.now() - self.user.date_joined).days
        
        # Last login
        last_login = self.user.last_login
        
        # Days since last login
        days_since_login = None
        if last_login:
            days_since_login = (timezone.now() - last_login).days
        
        # Account status
        is_active = self.user.is_active
        
        return {
            'account_age_days': account_age_days,
            'last_login': last_login,
            'days_since_login': days_since_login,
            'is_active': is_active,
        }
    
    def get_comprehensive_stats(self):
        """Get all user statistics in one call"""
        return {
            'gaming': self.get_gaming_stats(),
            'financial': self.get_financial_stats(),
            'transactions': self.get_transaction_stats(),
            'withdrawals': self.get_withdrawal_requests(),
            'referrals': self.get_referral_stats(),
            'activity': self.get_activity_stats(),
        }
