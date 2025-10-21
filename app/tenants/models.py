from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid


class Tenant(models.Model):
    """
    Multi-tenant architecture - each tenant represents a separate gaming platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    
    # Tenant settings
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    
    # Business information
    company_name = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Branding
    logo_url = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#ff6b35')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#f7931e')
    
    # Settings
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=3, default='ETB')
    language = models.CharField(max_length=5, default='en')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['domain']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    def soft_delete(self):
        """Soft delete the tenant"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    @property
    def is_trial_expired(self):
        """Check if trial period has expired"""
        if not self.is_trial or not self.trial_ends_at:
            return False
        return timezone.now() > self.trial_ends_at


class SubscriptionPlan(models.Model):
    """
    Subscription plans for tenants
    """
    PLAN_TYPES = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Limits
    max_users = models.PositiveIntegerField(default=100)
    max_games_per_day = models.PositiveIntegerField(default=1000)
    max_storage_gb = models.PositiveIntegerField(default=10)
    
    # Features
    features = models.JSONField(default=dict, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"


class TenantSubscription(models.Model):
    """
    Tenant subscription management
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Billing
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    next_billing_date = models.DateTimeField()
    
    # Payment
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tenant Subscription'
        verbose_name_plural = 'Tenant Subscriptions'
    
    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name}"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.current_period_start <= now <= self.current_period_end
        )


class TenantSettings(models.Model):
    """
    Tenant-specific settings and configurations
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    
    # Game settings
    default_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    max_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    min_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    
    # Fake player settings
    max_fake_players = models.PositiveIntegerField(default=50)
    fake_player_threshold = models.PositiveIntegerField(default=10)
    fake_players_can_win = models.BooleanField(default=True)
    
    # Game timing
    countdown_duration = models.PositiveIntegerField(default=30)  # seconds
    game_speed = models.PositiveIntegerField(default=5000)  # milliseconds
    
    # Financial settings
    house_edge_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=22.00)
    min_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    max_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    
    # Referral settings
    referral_bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    signup_bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Security settings
    max_login_attempts = models.PositiveIntegerField(default=5)
    session_timeout = models.PositiveIntegerField(default=3600)  # seconds
    
    # Custom settings (JSON field for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tenant Settings'
        verbose_name_plural = 'Tenant Settings'
    
    def __str__(self):
        return f"Settings for {self.tenant.name}"