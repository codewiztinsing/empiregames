from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group, Permission
from decimal import Decimal
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    def create_user(self, username, phone, telegram_id, password=None, **extra_fields):
        """Create a new user with phone and telegram_id"""
        if not username:
            raise ValueError('The username must be set')
        if not phone:
            raise ValueError('The phone must be set')
        if not telegram_id:
            raise ValueError('The telegram_id must be set')
        
        user = self.model(
            username=username,
            phone=phone,
            telegram_id=telegram_id,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, phone, telegram_id, password=None, **extra_fields):
        """Create a new superuser with phone and telegram_id"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, phone, telegram_id, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()
    
    phone = models.CharField(max_length=15, unique=True)
    telegram_id = models.CharField(max_length=15, unique=True)
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


