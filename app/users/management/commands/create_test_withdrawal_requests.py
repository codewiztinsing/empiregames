from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import WithdrawalRequest
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test WithdrawalRequest records for admin interface testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of withdrawal requests to create (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get all users
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(
                self.style.ERROR('No users found in the database')
            )
            return

        created_count = 0
        
        for i in range(count):
            # Select a random user
            user = random.choice(users)
            
            # Generate random withdrawal amount (500-5000 Birr - minimum is 500)
            amount = Decimal(str(random.randint(500, 5000)))
            
            # Generate random status
            statuses = ['pending', 'approved', 'rejected', 'completed']
            weights = [0.4, 0.2, 0.2, 0.2]  # More pending requests
            status = random.choices(statuses, weights=weights)[0]
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                user=user,
                amount=float(amount),
                status=status,
                admin_notes=f"Test withdrawal request #{i+1} - Generated for testing purposes"
            )
            
            created_count += 1
            self.stdout.write(f"Created withdrawal request: {amount} Birr for {user.username} (Status: {status})")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} withdrawal requests'
            )
        )
        
        # Show statistics
        total_requests = WithdrawalRequest.objects.count()
        pending_requests = WithdrawalRequest.objects.filter(status='pending').count()
        approved_requests = WithdrawalRequest.objects.filter(status='approved').count()
        rejected_requests = WithdrawalRequest.objects.filter(status='rejected').count()
        completed_requests = WithdrawalRequest.objects.filter(status='completed').count()
        
        self.stdout.write(f"\nWithdrawal Request Statistics:")
        self.stdout.write(f"• Total Requests: {total_requests}")
        self.stdout.write(f"• Pending: {pending_requests}")
        self.stdout.write(f"• Approved: {approved_requests}")
        self.stdout.write(f"• Rejected: {rejected_requests}")
        self.stdout.write(f"• Completed: {completed_requests}")
