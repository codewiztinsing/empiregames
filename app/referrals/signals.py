from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from wallet.models import Transaction
from .services import ReferralService

@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    """Handle new user registration and set as agent if no sponsor"""
    if created and not instance.sponsor:
        instance.is_agent = True
        instance.save()

@receiver(post_save, sender=Transaction)
def handle_transaction(sender, instance, created, **kwargs):
    """Handle transaction events for referral system"""
    if created:
        if instance.type == 'WIN' and instance.status == 'success':
            # Calculate referral bonuses when user wins
            ReferralService.calculate_referral_bonuses(
                instance.user, 
                instance.amount,
                getattr(instance, 'game_id', None)
            )
        elif instance.type == 'BET':
            # Update game statistics when user plays
            ReferralService.update_user_game_stats(instance.user)
