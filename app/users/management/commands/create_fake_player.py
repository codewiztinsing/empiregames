from django.core.management.base import BaseCommand
from users.models import User
from wallet.models import Wallet

class Command(BaseCommand):
    help = 'Create a fixed fake player account for transaction purposes'

    def handle(self, *args, **options):
        # Fixed fake player details
        FAKE_PLAYER_ID = 9999999999
        FAKE_PLAYER_NAME = "FakePlayer"
        FAKE_PLAYER_PHONE = "9999999999"
        FAKE_PLAYER_TELEGRAM = "9999999999"
        
        try:
            # Check if fake player already exists
            fake_player, created = User.objects.get_or_create(
                id=FAKE_PLAYER_ID,
                defaults={
                    'username': FAKE_PLAYER_NAME,
                    'phone': FAKE_PLAYER_PHONE,
                    'telegram_id': FAKE_PLAYER_TELEGRAM,
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            
            if created:
                # Create wallet for fake player
                Wallet.objects.get_or_create(
                    user=fake_player,
                    defaults={
                        'balance': 0.00,
                        'total_deposits': 0.00,
                        'total_withdrawals': 0.00,
                        'total_winnings': 0.00,
                        'total_bets': 0.00,
                    }
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created fake player: {fake_player.username} (ID: {fake_player.id})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Fake player already exists: {fake_player.username} (ID: {fake_player.id})')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating fake player: {str(e)}')
            )
