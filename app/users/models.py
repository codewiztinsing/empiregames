from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator


def generate_referral_code():
    return get_random_string(15)


class UserManager(BaseUserManager):
    def create_user(self, username, phone=None, telegram_id=None, password=None, tenant=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        
        # Provide default values for development
        phone = phone or f"251{get_random_string(9, '0123456789')}"
        telegram_id = telegram_id or get_random_string(10, '0123456789')
        
        user = self.model(
            username=username,
            phone=phone,
            telegram_id=telegram_id,
            tenant=tenant,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone=None, telegram_id=None, password=None, tenant=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, phone, telegram_id, password, tenant, **extra_fields)


class User(AbstractUser):
    """
    Enhanced User model with multi-tenancy support
    """
    objects = UserManager()
    
    # Multi-tenancy - will be added when tenants app is created
    # tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='users')
    
    # Core fields
    phone = models.CharField(max_length=15, unique=True)
    telegram_id = models.CharField(max_length=15, unique=True)
    
    # Referral system
    referral_code = models.CharField(max_length=15, default=generate_referral_code)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # User roles
    is_agent = models.BooleanField(default=False)
    is_tenant_admin = models.BooleanField(default=False)
    

    
    # Financial fields
    total_referral_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unwithdrawable_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
 
    # Game statistics
    total_games_played = models.PositiveIntegerField(default=0)
    games_played_today = models.PositiveIntegerField(default=0)
    games_played_this_week = models.PositiveIntegerField(default=0)
    last_game_date = models.DateField(null=True, blank=True)
    last_week_reset = models.DateField(null=True, blank=True)
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Override groups and permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='empire_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='empire_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            # Will add tenant index when tenant field is added
            models.Index(fields=['phone']),
            models.Index(fields=['telegram_id']),
            models.Index(fields=['referral_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username}"

    def soft_delete(self):
        """Soft delete the user"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.account_locked_until:
            return False
        return timezone.now() < self.account_locked_until

    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()

    def unlock_account(self):
        """Unlock the account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save()

    def record_failed_login(self):
        """Record a failed login attempt"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save()

    def reset_failed_logins(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save()


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=True, null=True)
    
    # Contact information
    email = models.EmailField(blank=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Location
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Preferences
    language = models.CharField(max_length=5, default='en')
    currency = models.CharField(max_length=3, default='ETB')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    
    # Profile settings
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Privacy settings
    profile_public = models.BooleanField(default=False)
    show_game_stats = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class UserSession(models.Model):
    """
    Track user sessions for security and analytics
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    
    # Session information
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Location (if available)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Session status
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.username} - {self.ip_address}"
    
    @property
    def is_expired(self):
        """Check if session has expired"""
        return timezone.now() > self.expires_at
    
    def deactivate(self):
        """Deactivate the session"""
        self.is_active = False
        self.save()


class SupportUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('admin', 'Customer Support'), ('support', 'Balance Manager')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# ReferralBonus model removed

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


class TelegramUser(models.Model):
    """
    Standalone Telegram user model for better separation of concerns
    """
    # Primary key
    id = models.BigAutoField(primary_key=True)
    
    # Telegram-specific fields
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    
    # Telegram user status
    is_bot = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Profile information
    photo_url = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Relationship to main User model
    linked_user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='telegram_profile'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        display_name = self.username or f"{self.first_name} {self.last_name}".strip() or f"User {self.telegram_id}"
        return f"{display_name} ({self.telegram_id})"
    
    @property
    def full_name(self):
        """Get the full name of the Telegram user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"
    
    @property
    def display_name(self):
        """Get the best available display name"""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    def soft_delete(self):
        """Soft delete the Telegram user"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def link_to_user(self, user):
        """Link this Telegram user to a main User account"""
        if self.linked_user and self.linked_user != user:
            raise ValueError("This Telegram user is already linked to another account")
        self.linked_user = user
        self.save()
    
    def unlink_from_user(self):
        """Unlink this Telegram user from the main User account"""
        self.linked_user = None
        self.save()
    
    @classmethod
    def get_or_create_from_telegram_data(cls, telegram_data):
        """
        Create or update TelegramUser from Telegram API data
        """
        telegram_id = telegram_data.get('id')
        if not telegram_id:
            raise ValueError("Telegram ID is required")
        
        defaults = {
            'username': telegram_data.get('username'),
            'first_name': telegram_data.get('first_name'),
            'last_name': telegram_data.get('last_name'),
            'language_code': telegram_data.get('language_code'),
            'is_bot': telegram_data.get('is_bot', False),
            'is_premium': telegram_data.get('is_premium', False),
            'is_verified': telegram_data.get('is_verified', False),
        }
        
        telegram_user, created = cls.objects.get_or_create(
            telegram_id=telegram_id,
            defaults=defaults
        )
        
        # Update fields if not created
        if not created:
            for key, value in defaults.items():
                if value is not None:
                    setattr(telegram_user, key, value)
            telegram_user.save()
        
        return telegram_user, created
