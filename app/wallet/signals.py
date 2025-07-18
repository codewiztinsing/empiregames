import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import transfer_funds
from .models import ChapaSession, Transaction, Wallet
from users.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Transaction)
def update_wallet_on_deposit(sender, instance, created, **kwargs):
    """
    Signal handler for updating wallet balance when transaction type is DEPOSIT and status is success.
    """
    print(f"Transaction: {instance.type}, {instance.status}")
    if instance.type == "DEPOSIT" and instance.status == "success":
        try:
            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(user=instance.user)
                wallet.balance += float(instance.amount)
                wallet.save()
                logger.info(f"Wallet balance updated for user {instance.user.username}. New balance: {wallet.balance}")
                return wallet
        except Exception as e:
            logger.error(f"Error updating wallet for user {instance.user.username}: {str(e)}")
            return None
    return None
   

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
        chapa_response = transfer_funds(receiver_name, instance.user.phone, instance.amount, "ETB", instance.reference, 855)
        print(chapa_response)
        
        
    return None
  