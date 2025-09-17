from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group, Permission

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    telegram_id = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=15, default=get_random_string(15))
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


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_received')
    referral_code_used = models.CharField(max_length=15)
    bonus_amount = models.FloatField(default=5.0)
    bonus_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"


class Contact(models.Model):
    ROLE_CHOICES = [
        ('game_manager', 'Game Manager'),
        ('support', 'Customer Support'),
        ('admin', 'Administrator'),
        ('moderator', 'Game Moderator'),
        ('supervisor', 'Supervisor'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50, default='Operations')
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(default=list, help_text="List of specific permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contacts')
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"
    
    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
