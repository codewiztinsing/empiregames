from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wallet.models import Transaction
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test pending withdrawal requests for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of pending withdrawal requests to create (default: 5)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to create requests for (optional)'
        )

    def handle(self, *args, **options):
        count = options['count']
        user_id = options.get('user_id')
        
        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
                self.stdout.write(f"Creating requests for user ID: {user_id}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {user_id} does not exist')
                )
                return
        else:
            # Get all users who have wallets
            users = User.objects.all()[:10]  # Limit to first 10 users
            if not users.exists():
                self.stdout.write(
                    self.style.ERROR('No users found in the database')
                )
                return

        created_count = 0
        
        for i in range(count):
            # Select a random user
            user = random.choice(users)
            
            # Generate random withdrawal amount (50-1000 Birr)
            amount = Decimal(str(random.randint(50, 1000)))
            
            # Generate random reference
            reference = f"WDR_{user.id}_{i+1}_{random.randint(1000, 9999)}"
            
            # Create pending withdrawal transaction
            transaction = Transaction.objects.create(
                user=user,
                amount=float(amount),
                type='WITHDRAW',
                status='pending',
                reference=reference
            )
            
            created_count += 1
            self.stdout.write(f"Created pending withdrawal: {amount} Birr for {user.username} (ID: {user.id})")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} pending withdrawal requests'
            )
        )
        
        # Show statistics
        total_pending = Transaction.objects.filter(
            type='WITHDRAW',
            status='pending'
        ).count()
        
        self.stdout.write(f"Total pending withdrawal requests: {total_pending}")
