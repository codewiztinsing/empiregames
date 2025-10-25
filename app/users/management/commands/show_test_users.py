from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import WithdrawalRequest

User = get_user_model()

class Command(BaseCommand):
    help = 'Show test user information for bot testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to show information for'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.show_user_info(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {user_id} does not exist')
                )
        else:
            # Show all test users
            test_users = User.objects.filter(username__startswith='test_player')
            self.stdout.write(f"Test Users ({test_users.count()} total):\n")
            
            for user in test_users:
                self.show_user_info(user)
                self.stdout.write("")

    def show_user_info(self, user):
        """Show user information and their withdrawal requests"""
        self.stdout.write(f"👤 User: {user.username}")
        self.stdout.write(f"   ID: {user.id}")
        self.stdout.write(f"   Telegram ID: {user.telegram_id}")
        self.stdout.write(f"   Phone: {user.phone}")
        
        # Show withdrawal requests
        withdrawals = WithdrawalRequest.objects.filter(user=user)
        pending_count = withdrawals.filter(status='pending').count()
        
        self.stdout.write(f"   Withdrawal Requests: {withdrawals.count()} total, {pending_count} pending")
        
        if pending_count > 0:
            self.stdout.write(f"   Pending Requests:")
            for w in withdrawals.filter(status='pending'):
                self.stdout.write(f"     - {w.amount} Birr (ID: {w.id})")
        
        self.stdout.write("")
