from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

from django.contrib.auth.models import Group, Permission
class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    telegram_id = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=15, default=get_random_string(15))
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
