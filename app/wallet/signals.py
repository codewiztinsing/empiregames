import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import transfer_funds
from .models import ChapaSession, Transaction, Wallet
from users.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ChapaSession)
def chapa_session_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for processing successful Chapa payments.
    Creates a transaction and updates user's wallet balance upon successful payment.
    """
    # Only process if this is a successful payment session
    if instance.status != "success":
        return

    logger.info(
        f"Processing successful ChapaSession for {instance.phone_number}. "
        f"Amount: {instance.amount}, Reference: {instance.trx_ref}"
    )

    try:
        with transaction.atomic():
            # Get user with related objects selected
            user = User.objects.select_related('wallet').get(phone=instance.phone_number)
            
            # Validate amount is positive
            if instance.amount <= 0:
                raise ValidationError(f"Invalid amount: {instance.amount}. Amount must be positive.")

            # Create transaction record
            transaction_record = Transaction.objects.create(
                user=user,
                amount=instance.amount,
                type="CREDIT",
                status="success",
                reference=instance.trx_ref
            )

            # Get or create wallet (handles case where wallet doesn't exist)
            wallet, created = Wallet.objects.get_or_create(
                user=user,
                defaults={'balance': instance.amount}
            )

            if not created:
                # Update existing wallet
                wallet.balance += instance.amount
                wallet.save(update_fields=['balance'])

            logger.info(
                f"Successfully processed payment. User: {user.id}, "
                f"Transaction: {transaction_record.id}, "
                f"New balance: {wallet.balance}"
            )

    except ObjectDoesNotExist as e:
        logger.error(
            f"User not found for phone number: {instance.phone_number}. "
            f"ChapaSession ID: {instance.id}. Error: {str(e)}"
        )
        # Consider adding notification to admin here

    except ValidationError as e:
        logger.error(
            f"Validation error for ChapaSession {instance.id}: {str(e)}. "
            f"Amount: {instance.amount}"
        )
        # Consider adding notification to admin here

    except Exception as e:
        logger.error(
            f"Unexpected error processing ChapaSession {instance.id}: {str(e)}",
            exc_info=True
        )
        

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
  