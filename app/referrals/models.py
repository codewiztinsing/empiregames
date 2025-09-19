from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class ReferralBonus(models.Model):
    """Track referral bonuses earned from wins"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_bonuses')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses_given')
    generation = models.IntegerField(choices=[(1, 'First Generation'), (2, 'Second Generation')])
    win_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # 4% or 1%
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    game_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid')
    ], default='pending')

    class Meta:
        verbose_name = "Referral Bonus"
        verbose_name_plural = "Referral Bonuses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.bonus_amount} from {self.from_user.username}"

class ReferralWithdrawal(models.Model):
    """Track withdrawal requests for referral bonuses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Referral Withdrawal"
        verbose_name_plural = "Referral Withdrawals"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

class UserGameStats(models.Model):
    """Track user game statistics for withdrawal eligibility"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='game_stats')
    games_played_today = models.IntegerField(default=0)
    games_played_this_week = models.IntegerField(default=0)
    last_game_date = models.DateField(null=True, blank=True)
    last_week_reset = models.DateField(null=True, blank=True)
    total_games_played = models.IntegerField(default=0)
    total_winnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_referral_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "User Game Stats"
        verbose_name_plural = "User Game Stats"

    def __str__(self):
        return f"{self.user.username} - Games: {self.total_games_played}"

class ReferralSettings(models.Model):
    """Global settings for referral system"""
    first_generation_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=4.00)  # 4%
    second_generation_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)  # 1%
    minimum_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)  # 500 birr
    daily_games_required = models.IntegerField(default=3)
    weekly_games_required = models.IntegerField(default=27)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Referral Settings"
        verbose_name_plural = "Referral Settings"

    def __str__(self):
        return f"Referral Settings - {self.first_generation_bonus}% / {self.second_generation_bonus}%"

    @classmethod
    def get_settings(cls):
        """Get current referral settings, create if not exists"""
        settings, created = cls.objects.get_or_create(
            is_active=True,
            defaults={
                'first_generation_bonus': 4.00,
                'second_generation_bonus': 1.00,
                'minimum_withdrawal': 500.00,
                'daily_games_required': 3,
                'weekly_games_required': 27,
            }
        )
        return settings