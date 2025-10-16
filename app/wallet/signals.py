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
    # Legacy withdraw auto-payout removed
        
        
    return None
  