from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class FeatureFlag(models.Model):
    """
    Feature flags for controlling functionality per tenant
    """
    FLAG_TYPES = [
        ('boolean', 'Boolean'),
        ('string', 'String'),
        ('number', 'Number'),
        ('json', 'JSON'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='feature_flags')
    
    # Flag details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPES, default='boolean')
    
    # Flag value
    boolean_value = models.BooleanField(default=False)
    string_value = models.CharField(max_length=500, blank=True, null=True)
    number_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    json_value = models.JSONField(default=dict, blank=True)
    
    # Flag status
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)  # Apply to all tenants
    
    # Targeting
    target_users = models.ManyToManyField('users.User', blank=True, related_name='feature_flags')
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_feature_flags')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'
        unique_together = ['tenant', 'name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['is_global', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"
    
    def get_value(self):
        """Get the appropriate value based on flag type"""
        if self.flag_type == 'boolean':
            return self.boolean_value
        elif self.flag_type == 'string':
            return self.string_value
        elif self.flag_type == 'number':
            return self.number_value
        elif self.flag_type == 'json':
            return self.json_value
        return None
    
    def is_enabled_for_user(self, user):
        """Check if feature flag is enabled for a specific user"""
        if not self.is_active:
            return False
        
        if self.is_global:
            return True
        
        if self.target_users.filter(id=user.id).exists():
            return True
        
        # Check percentage targeting
        if self.target_percentage < 100.00:
            # Simple hash-based percentage targeting
            user_hash = hash(f"{user.id}_{self.name}") % 100
            return user_hash < self.target_percentage
        
        return True


class UsageLimit(models.Model):
    """
    Usage limits and quotas for tenants
    """
    LIMIT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('total', 'Total'),
    ]
    
    RESOURCE_TYPES = [
        ('games', 'Games'),
        ('users', 'Users'),
        ('transactions', 'Transactions'),
        ('storage', 'Storage'),
        ('api_calls', 'API Calls'),
        ('bandwidth', 'Bandwidth'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='usage_limits')
    
    # Limit details
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    limit_type = models.CharField(max_length=20, choices=LIMIT_TYPES)
    limit_value = models.PositiveIntegerField()
    current_usage = models.PositiveIntegerField(default=0)
    
    # Limit settings
    is_active = models.BooleanField(default=True)
    is_hard_limit = models.BooleanField(default=True)  # Hard limit blocks usage, soft limit allows with warnings
    warning_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80.00)  # Percentage
    
    # Reset information
    last_reset = models.DateTimeField(auto_now_add=True)
    next_reset = models.DateTimeField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['resource_type', 'limit_type']
        verbose_name = 'Usage Limit'
        verbose_name_plural = 'Usage Limits'
        unique_together = ['tenant', 'resource_type', 'limit_type']
        indexes = [
            models.Index(fields=['tenant', 'resource_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.resource_type} - {self.limit_type} - {self.current_usage}/{self.limit_value}"
    
    def is_exceeded(self):
        """Check if usage limit is exceeded"""
        return self.current_usage >= self.limit_value
    
    def is_warning_threshold_reached(self):
        """Check if warning threshold is reached"""
        threshold = (self.limit_value * self.warning_threshold) / 100
        return self.current_usage >= threshold
    
    def increment_usage(self, amount=1):
        """Increment current usage"""
        self.current_usage += amount
        self.save()
    
    def reset_usage(self):
        """Reset current usage"""
        self.current_usage = 0
        self.last_reset = timezone.now()
        self.save()


class UsageTracking(models.Model):
    """
    Track actual usage for monitoring and billing
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='usage_tracking')
    
    # Usage details
    resource_type = models.CharField(max_length=20, choices=UsageLimit.RESOURCE_TYPES)
    usage_amount = models.PositiveIntegerField()
    usage_unit = models.CharField(max_length=20, default='count')
    
    # Context
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    game = models.ForeignKey('game.Game', on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey('finance.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Time information
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Usage Tracking'
        verbose_name_plural = 'Usage Tracking'
        indexes = [
            models.Index(fields=['tenant', 'resource_type', 'date']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.resource_type} - {self.usage_amount} - {self.timestamp}"


class Settings(models.Model):
    """
    Tenant-specific settings and configurations
    """
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='feature_settings')
    
    # General settings
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=5, default='en')
    currency = models.CharField(max_length=3, default='ETB')
    
    # Business settings
    company_name = models.CharField(max_length=200, blank=True, null=True)
    support_email = models.EmailField(blank=True, null=True)
    support_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Branding settings
    logo_url = models.URLField(blank=True, null=True)
    favicon_url = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#ff6b35')
    secondary_color = models.CharField(max_length=7, default='#f7931e')
    
    # Security settings
    password_min_length = models.PositiveIntegerField(default=8)
    password_require_special = models.BooleanField(default=True)
    session_timeout = models.PositiveIntegerField(default=3600)  # seconds
    max_login_attempts = models.PositiveIntegerField(default=5)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Custom settings (JSON field for flexibility)
    custom_settings = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'
    
    def __str__(self):
        return f"Settings for {self.tenant.name}"