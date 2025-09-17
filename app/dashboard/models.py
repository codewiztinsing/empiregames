from django.db import models
from django.contrib.auth.models import User as DjangoUser

# Create your models here.

class BroadcastMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    message = models.TextField()
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Broadcast Message"
        verbose_name_plural = "Broadcast Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Broadcast {self.id} - {self.status}"
    
    @property
    def progress_percentage(self):
        if self.total_recipients == 0:
            return 0
        return round((self.sent_count + self.failed_count) / self.total_recipients * 100, 2)
