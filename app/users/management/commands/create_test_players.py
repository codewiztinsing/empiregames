from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Agent
import random
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test players under agent ID 1 for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of test players to create (default: 10)'
        )
        parser.add_argument(
            '--agent-id',
            type=int,
            default=1,
            help='Agent ID to assign players to (default: 1)'
        )

    def handle(self, *args, **options):
        count = options['count']
        agent_id = options['agent_id']
        
        try:
            agent = Agent.objects.get(id=agent_id)
            self.stdout.write(f"Found agent: {agent.user.username} (ID: {agent_id})")
        except Agent.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Agent with ID {agent_id} does not exist')
            )
            return

        created_count = 0
        
        for i in range(count):
            # Generate random username
            username = f"test_player_{i+1}_{''.join(random.choices(string.ascii_lowercase, k=4))}"
            
            # Generate random phone number
            phone = f"09{random.randint(10000000, 99999999)}"
            
            # Generate random telegram ID (avoiding existing ones)
            telegram_id = random.randint(100000000, 999999999)
            
            # Check if telegram_id already exists
            while User.objects.filter(telegram_id=telegram_id).exists():
                telegram_id = random.randint(100000000, 999999999)
            
            # Create user
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': username,
                    'phone': phone,
                    'first_name': f"Test Player {i+1}",
                    'last_name': f"Last{i+1}",
                    'email': f"{username}@test.com",
                    'referred_by': agent.user,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created test player: {username} (Telegram ID: {telegram_id})")
            else:
                self.stdout.write(f"Player already exists: {username}")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test players under agent {agent.user.username} (ID: {agent_id})'
            )
        )
        
        # Show statistics
        total_referrals = User.objects.filter(referred_by=agent.user).count()
        self.stdout.write(f"Total referrals for agent {agent.user.username}: {total_referrals}")