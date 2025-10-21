from django.db import models
from django.utils import timezone
from users.models import User


class Banner(models.Model):
    image = models.ImageField(upload_to='promotions/banners/', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banners')


    def __str__(self):
        return f"{self.image}"





class Promotion(models.Model):
    PROMOTION_TYPES = [
        ('banner', 'Banner'),
        ('popup', 'Popup'),
        ('notification', 'Notification'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('scheduled', 'Scheduled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, default='banner')
    banner_image = models.ForeignKey(Banner, on_delete=models.SET_NULL, null=True, blank=True)
    # Promotion details
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        now = timezone.now()
        
        if self.status != 'active':
            return False
            
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_click_count(self):
        self.click_count += 1
        self.save(update_fields=['click_count'])
