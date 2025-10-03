import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from wallet.models import Wallet

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal handler to create a wallet with balance 0 when a new user is created.
    """
    if created:
        try:
            Wallet.objects.create(user=instance, balance=0)
            logger.info(f"Wallet created for user {instance.username} (ID: {instance.id})")
        except Exception as e:
            logger.error(f"Failed to create wallet for user {instance.username}: {str(e)}")
