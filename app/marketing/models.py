from django.db import models
from django.utils import timezone


class Advertisement(models.Model):
    GAME_TYPES = [
        ('bingo', 'Bingo'),
        ('lottery', 'Lottery'),
        ('slots', 'Slots'),
        ('poker', 'Poker'),
        ('roulette', 'Roulette'),
        ('blackjack', 'Blackjack'),
        ('other', 'Other'),
    ]
    
    AD_TYPES = [
        ('banner', 'Banner'),
        ('popup', 'Popup'),
        ('interstitial', 'Interstitial'),
        ('video', 'Video'),
        ('native', 'Native'),
        ('sponsored', 'Sponsored Content'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    advertiser_name = models.CharField(max_length=100)
    advertiser_email = models.EmailField()
    
    # Ad Content
    ad_type = models.CharField(max_length=20, choices=AD_TYPES, default='banner')
    image_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    click_url = models.URLField()
    
    # Game Targeting
    target_game_types = models.JSONField(default=list, help_text="List of game types to target")
    min_player_level = models.IntegerField(default=1)
    max_player_level = models.IntegerField(default=100)
    
    # Scheduling
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Budget & Pricing
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_click = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    cost_per_impression = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    daily_budget_limit = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Targeting Options
    target_countries = models.JSONField(default=list, help_text="List of country codes")
    target_languages = models.JSONField(default=list, help_text="List of language codes")
    target_age_min = models.IntegerField(default=18)
    target_age_max = models.IntegerField(default=99)
    
    # Display Settings
    max_impressions_per_user = models.IntegerField(default=3)
    display_frequency_hours = models.IntegerField(default=24, help_text="Hours between showing same ad to user")
    priority = models.IntegerField(default=1, help_text="Higher number = higher priority")
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_impressions = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['target_game_types']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.advertiser_name}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.status == 'active' and
            self.start_date <= now <= self.end_date and
            self.total_spend < self.budget
        )
    
    @property
    def click_through_rate(self):
        if self.total_impressions > 0:
            return (self.total_clicks / self.total_impressions) * 100
        return 0.0
    
    def can_show_to_user(self, user_profile):
        """Check if this ad can be shown to a specific user"""
        if not self.is_active:
            return False
        
        # Check daily budget
        if self.daily_budget_limit:
            today = timezone.now().date()
            daily_spend = AdImpression.objects.filter(
                advertisement=self,
                created_at__date=today
            ).aggregate(
                total=models.Sum('cost')
            )['total'] or 0
            
            if daily_spend >= self.daily_budget_limit:
                return False
        
        # Check user impression frequency
        if self.max_impressions_per_user > 0:
            cutoff_time = timezone.now() - timezone.timedelta(hours=self.display_frequency_hours)
            recent_impressions = AdImpression.objects.filter(
                advertisement=self,
                user_id=user_profile.telegram_id,
                created_at__gte=cutoff_time
            ).count()
            
            if recent_impressions >= self.max_impressions_per_user:
                return False
        
        return True


class AdImpression(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='impressions')
    user_id = models.BigIntegerField()  # Telegram user ID
    user_country = models.CharField(max_length=2, blank=True)
    user_language = models.CharField(max_length=5, blank=True)
    game_type = models.CharField(max_length=20, blank=True)
    
    # Tracking Data
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Cost tracking
    cost = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['advertisement', 'user_id', 'created_at']),
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Impression: {self.advertisement.title} - User {self.user_id}"


class AdClick(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='clicks')
    impression = models.OneToOneField(AdImpression, on_delete=models.CASCADE, related_name='click')
    user_id = models.BigIntegerField()  # Telegram user ID
    
    # Tracking Data
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Cost tracking
    cost = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['advertisement', 'created_at']),
            models.Index(fields=['user_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"Click: {self.advertisement.title} - User {self.user_id}"


class AdCampaign(models.Model):
    CAMPAIGN_TYPES = [
        ('awareness', 'Brand Awareness'),
        ('acquisition', 'User Acquisition'),
        ('retention', 'Player Retention'),
        ('monetization', 'Monetization'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    
    # Budget
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_spend(self):
        return self.advertisements.aggregate(
            total=models.Sum('total_spend')
        )['total'] or 0
    
    @property
    def total_impressions(self):
        return self.advertisements.aggregate(
            total=models.Sum('total_impressions')
        )['total'] or 0
    
    @property
    def total_clicks(self):
        return self.advertisements.aggregate(
            total=models.Sum('total_clicks')
        )['total'] or 0


# Add campaign relationship to Advertisement
Advertisement.add_to_class(
    'campaign',
    models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='advertisements', blank=True, null=True)
)

