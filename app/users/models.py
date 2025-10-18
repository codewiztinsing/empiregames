from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group, Permission
from decimal import Decimal
from django.core.validators import MinValueValidator

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    telegram_id = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=15, default=get_random_string(15))
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    is_agent = models.BooleanField(default=False)  # Default to customer, not agent
    sponsor_changed = models.BooleanField(default=False)  # Can only change once
    total_referral_earnings = models.FloatField(default=0.00)
    signup_bonus_claimed = models.BooleanField(default=False)  # Track if signup bonus was claimed
    sponsor_change_bonus_claimed = models.BooleanField(default=False)  # Track if sponsor change bonus was claimed
    unwithdrawable_bonus = models.FloatField(default=0.00)  # Bonus that can be used to play
    total_games_played = models.PositiveIntegerField(default=0)
    games_played_today = models.PositiveIntegerField(default=0)
    games_played_this_week = models.PositiveIntegerField(default=0)
    last_game_date = models.DateField(null=True, blank=True)
    last_week_reset = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='wow_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='wow_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username


class SupportUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('admin', 'Customer Support'), ('support', 'Balance Manager')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class ReferralBonus(models.Model):
    BONUS_TYPE_CHOICES = [
        ('first_generation', 'First Generation (4%)'),
        ('second_generation', 'Second Generation (1%)'),
        ('signup', 'Signup Bonus (10 birr)'),
        ('sponsor_change', 'Sponsor Change Bonus (9 birr)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_bonuses')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='win_bonuses')
    game_id = models.CharField(max_length=100)
    win_amount = models.FloatField()
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    bonus_amount = models.FloatField()
    generation_level = models.PositiveIntegerField()  # 1 for first generation, 2 for second
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referrer.username} - {self.bonus_type} - {self.bonus_amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.FloatField(
        validators=[MinValueValidator(Decimal('500.00'))]  # Minimum 500 birr
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"


class ReferralAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
