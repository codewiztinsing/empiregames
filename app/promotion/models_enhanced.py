from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Banner(models.Model):
    """
    Enhanced banner system with multi-tenancy
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='banners')
    
    # Banner details
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='promotions/banners/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    
    # Banner settings
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # Targeting
    target_audience = models.CharField(max_length=50, choices=[
        ('all', 'All Users'),
        ('new', 'New Users'),
        ('returning', 'Returning Users'),
        ('vip', 'VIP Users'),
        ('custom', 'Custom'),
    ], default='all')
    
    # Display settings
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    max_displays = models.PositiveIntegerField(null=True, blank=True)
    current_displays = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"
    
    def soft_delete(self):
        """Soft delete the banner"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    @property
    def is_currently_active(self):
        """Check if banner is currently active"""
        now = timezone.now()
        
        if not self.is_active or self.is_deleted:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        if self.max_displays and self.current_displays >= self.max_displays:
            return False
        
        return True


class Promotion(models.Model):
    """
    Enhanced promotion system with better tracking and analytics
    """
    PROMOTION_TYPES = [
        ('banner', 'Banner'),
        ('popup', 'Popup'),
        ('notification', 'Notification'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('scheduled', 'Scheduled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='promotions')
    
    # Promotion details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, default='popup')
    
    # Visual content
    banner_image = models.ForeignKey(Banner, on_delete=models.SET_NULL, null=True, blank=True)
    custom_image_url = models.URLField(blank=True, null=True)
    
    # Promotion details
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    maximum_bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    
    # Targeting
    target_audience = models.CharField(max_length=50, choices=[
        ('all', 'All Users'),
        ('new', 'New Users'),
        ('returning', 'Returning Users'),
        ('vip', 'VIP Users'),
        ('inactive', 'Inactive Users'),
        ('custom', 'Custom'),
    ], default='all')
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    
    # Limits
    max_displays = models.PositiveIntegerField(null=True, blank=True)
    max_clicks = models.PositiveIntegerField(null=True, blank=True)
    max_conversions = models.PositiveIntegerField(null=True, blank=True)
    
    # Campaign information
    campaign_id = models.CharField(max_length=100, blank=True, null=True)
    campaign_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['promotion_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['campaign_id']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def soft_delete(self):
        """Soft delete the promotion"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.status = 'cancelled'
        self.save()
    
    @property
    def is_active(self):
        """Check if promotion is currently active"""
        now = timezone.now()
        
        if self.status != 'active' or self.is_deleted:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        if self.max_displays and self.view_count >= self.max_displays:
            return False
        
        if self.max_clicks and self.click_count >= self.max_clicks:
            return False
        
        return True
    
    @property
    def click_through_rate(self):
        """Calculate click-through rate"""
        if self.view_count == 0:
            return 0.00
        return (self.click_count / self.view_count) * 100
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate"""
        if self.click_count == 0:
            return 0.00
        return (self.conversion_count / self.click_count) * 100
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_click_count(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    def increment_conversion_count(self):
        """Increment conversion count"""
        self.conversion_count += 1
        self.save(update_fields=['conversion_count'])


class Campaign(models.Model):
    """
    Marketing campaigns to group related promotions
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='campaigns')
    
    # Campaign details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Campaign timing
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    
    # Campaign goals
    target_views = models.PositiveIntegerField(null=True, blank=True)
    target_clicks = models.PositiveIntegerField(null=True, blank=True)
    target_conversions = models.PositiveIntegerField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Campaign metrics
    total_views = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    total_conversions = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"
    
    @property
    def click_through_rate(self):
        """Calculate overall click-through rate"""
        if self.total_views == 0:
            return 0.00
        return (self.total_clicks / self.total_views) * 100
    
    @property
    def conversion_rate(self):
        """Calculate overall conversion rate"""
        if self.total_clicks == 0:
            return 0.00
        return (self.total_conversions / self.total_clicks) * 100


class PromotionTracking(models.Model):
    """
    Track individual promotion interactions
    """
    ACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('conversion', 'Conversion'),
        ('dismiss', 'Dismiss'),
    ]
    
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='tracking')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='promotion_tracking')
    
    # Interaction details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # Additional context
    referrer = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Promotion Tracking'
        verbose_name_plural = 'Promotion Tracking'
        indexes = [
            models.Index(fields=['promotion', 'action_type']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.promotion.title} - {self.user.username} - {self.get_action_type_display()}"
