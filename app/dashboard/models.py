from django.db import models
from django.db.models import Sum
from users.models import User
from django.utils import timezone

# Create your models here.

class Agent(models.Model):
    """Agent model for managing agents who can refer users and earn commissions"""
    name = models.CharField(max_length=100, default="Unknown Agent", help_text="Agent's full name")
    phone = models.CharField(max_length=15, unique=True, default="", help_text="Agent's phone number")
    agent_code = models.CharField(max_length=20, unique=True, default="", help_text="Unique code for agent referrals")
    telegram_bot_link = models.URLField(blank=True, null=True, help_text="Unique Telegram bot link for this agent")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="Commission rate in percentage")
    is_active = models.BooleanField(default=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_referrals = models.IntegerField(default=0)
    total_deposits_referred = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Authentication fields
    username = models.CharField(max_length=150, unique=True, default="", help_text="Agent's login username")
    password = models.CharField(max_length=128, default="", help_text="Agent's login password (hashed)")
    email = models.EmailField(blank=True, null=True, help_text="Agent's email address")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
    
    def __str__(self):
        return f"Agent: {self.name} ({self.agent_code})"
    
    def calculate_commission(self, deposit_amount):
        """Calculate commission for a deposit amount"""
        return (deposit_amount * self.commission_rate) / 100
    
    def generate_telegram_bot_link(self):
        """Generate unique Telegram bot link for this agent"""
        from django.conf import settings
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'wowbingobotbotbot')
        return f"https://t.me/{bot_username}?start=agent_{self.agent_code}"
    
    def update_statistics(self):
        """Update agent statistics based on actual users registered with this agent code"""
        from users.models import User
        
        # Count users registered with this agent code
        users_with_agent_code = User.objects.filter(agent_code=self.agent_code)
        self.total_referrals = users_with_agent_code.count()
        
        # Calculate total deposits from referred users
        from wallet.models import Transaction
        total_deposits = Transaction.objects.filter(
            user__agent_code=self.agent_code,
            type='DEPOSIT',
            status='success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.total_deposits_referred = total_deposits
        
        # Calculate total earnings (simplified - no commission tracking)
        self.total_earnings = 0.00
        
        self.save(update_fields=['total_referrals', 'total_deposits_referred', 'total_earnings'])
    
    def set_password(self, raw_password):
        """Set the agent's password"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        """Override save to generate telegram bot link"""
        if not self.telegram_bot_link:
            self.telegram_bot_link = self.generate_telegram_bot_link()
        super().save(*args, **kwargs)


