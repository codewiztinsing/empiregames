import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, Wallet
from users.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

logger = logging.getLogger(__name__)



@receiver(post_save, sender=Transaction)
def transaction_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for processing transactions.
    Updates user's wallet balance upon successful transaction.
    """
    if instance.type == "WITHDRAW":
        print(f"Amount: {instance.amount}, Reference: {instance.reference}")
        print(f"User: {instance.user.username}, Phone: {instance.user.phone}")
        receiver_name = instance.user.first_name + instance.user.last_name
        print(f"Receiver Name: {receiver_name}")
        # Chapa transfer removed
        
        
    return None
  