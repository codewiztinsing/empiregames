from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class AuditLog(models.Model):
    """
    Comprehensive audit logging for all data changes
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('soft_delete', 'Soft Delete'),
        ('restore', 'Restore'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
        ('password_change', 'Password Change'),
        ('permission_change', 'Permission Change'),
        ('transaction', 'Transaction'),
        ('withdrawal', 'Withdrawal'),
        ('game_action', 'Game Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='audit_logs')
    
    # Action details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    
    # User information
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Object information (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Change details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['tenant', 'action_type']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.description} - {self.timestamp}"


class UserAnalytics(models.Model):
    """
    User behavior and engagement analytics
    """
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='analytics')
    
    # Login statistics
    total_logins = models.PositiveIntegerField(default=0)
    last_login_at = models.DateTimeField(null=True, blank=True)
    consecutive_login_days = models.PositiveIntegerField(default=0)
    longest_login_streak = models.PositiveIntegerField(default=0)
    
    # Game statistics
    total_games_played = models.PositiveIntegerField(default=0)
    total_games_won = models.PositiveIntegerField(default=0)
    total_bet_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_win_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Financial statistics
    total_deposits = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_withdrawals = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Referral statistics
    total_referrals = models.PositiveIntegerField(default=0)
    active_referrals = models.PositiveIntegerField(default=0)
    referral_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Engagement metrics
    average_session_duration = models.PositiveIntegerField(default=0)  # seconds
    total_session_time = models.PositiveIntegerField(default=0)  # seconds
    pages_viewed = models.PositiveIntegerField(default=0)
    
    # Risk metrics
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    suspicious_activity_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
        indexes = [
            models.Index(fields=['total_games_played']),
            models.Index(fields=['win_rate']),
            models.Index(fields=['risk_score']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.user.username}"
    
    def calculate_win_rate(self):
        """Calculate win rate percentage"""
        if self.total_games_played > 0:
            self.win_rate = (self.total_games_won / self.total_games_played) * 100
        else:
            self.win_rate = 0.00
        return self.win_rate
    
    def calculate_net_profit_loss(self):
        """Calculate net profit/loss"""
        self.net_profit_loss = self.total_win_amount - self.total_bet_amount
        return self.net_profit_loss


class GameStats(models.Model):
    """
    Game-level statistics and analytics
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='game_stats')
    
    # Time period
    date = models.DateField()
    period_type = models.CharField(max_length=10, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')
    
    # Game statistics
    total_games = models.PositiveIntegerField(default=0)
    completed_games = models.PositiveIntegerField(default=0)
    cancelled_games = models.PositiveIntegerField(default=0)
    
    # Player statistics
    total_players = models.PositiveIntegerField(default=0)
    unique_players = models.PositiveIntegerField(default=0)
    new_players = models.PositiveIntegerField(default=0)
    returning_players = models.PositiveIntegerField(default=0)
    
    # Financial statistics
    total_entry_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_prize_pool = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_house_edge = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    average_game_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Performance metrics
    average_game_duration = models.PositiveIntegerField(default=0)  # seconds
    average_players_per_game = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    games_per_hour = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Game Statistics'
        verbose_name_plural = 'Game Statistics'
        unique_together = ['tenant', 'date', 'period_type']
        indexes = [
            models.Index(fields=['tenant', 'date']),
            models.Index(fields=['period_type', 'date']),
        ]
    
    def __str__(self):
        return f"Game Stats - {self.tenant.name} - {self.date} ({self.period_type})"


class Metrics(models.Model):
    """
    System and business metrics
    """
    METRIC_TYPES = [
        ('revenue', 'Revenue'),
        ('users', 'Users'),
        ('games', 'Games'),
        ('performance', 'Performance'),
        ('system', 'System'),
        ('business', 'Business'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='metrics')
    
    # Metric details
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=100)
    metric_value = models.DecimalField(max_digits=15, decimal_places=4)
    metric_unit = models.CharField(max_length=20, blank=True, null=True)
    
    # Time information
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    
    # Additional context
    context = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Metric'
        verbose_name_plural = 'Metrics'
        indexes = [
            models.Index(fields=['tenant', 'metric_type']),
            models.Index(fields=['metric_name', 'date']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_name} - {self.metric_value} {self.metric_unit}"


class PerformanceLog(models.Model):
    """
    System performance monitoring
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='performance_logs')
    
    # Performance details
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    response_time = models.PositiveIntegerField()  # milliseconds
    status_code = models.PositiveIntegerField()
    
    # Request details
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # System information
    memory_usage = models.PositiveIntegerField(null=True, blank=True)  # MB
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # percentage
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Performance Log'
        verbose_name_plural = 'Performance Logs'
        indexes = [
            models.Index(fields=['tenant', 'endpoint']),
            models.Index(fields=['response_time']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.response_time}ms - {self.timestamp}"