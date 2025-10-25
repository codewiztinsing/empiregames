import random
from django.core.management.base import BaseCommand
from users.models import User
from game.models import CustomBingoCard


class Command(BaseCommand):
    help = 'Create test custom bingo cards for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of custom cards to create per user'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to create cards for'
        )

    def handle(self, *args, **options):
        count = options['count']
        user_id = options['user_id']
        
        # Get users to create cards for
        if user_id:
            users = User.objects.filter(id=user_id)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
                return
        else:
            # Get first 3 users or create test users
            users = User.objects.all()[:3]
            if not users.exists():
                self.stdout.write(self.style.WARNING("No users found. Please create some users first."))
                return
        
        # Column ranges for bingo
        column_ranges = {
            'B': (1, 15),
            'I': (16, 30),
            'N': (31, 45),
            'G': (46, 60),
            'O': (61, 75)
        }
        
        created_cards = 0
        
        for user in users:
            self.stdout.write(f"Creating custom cards for user: {user.username}")
            
            for i in range(count):
                # Generate random card numbers
                numbers = {}
                for column, (min_val, max_val) in column_ranges.items():
                    # Generate 5 unique random numbers for this column
                    column_numbers = []
                    while len(column_numbers) < 5:
                        num = random.randint(min_val, max_val)
                        if num not in column_numbers:
                            column_numbers.append(num)
                    numbers[column] = sorted(column_numbers)
                
                # Create card name
                card_name = f"Test Card {i + 1}"
                
                # Set first card as default
                is_default = i == 0
                
                # Create the custom card
                card = CustomBingoCard.objects.create(
                    user=user,
                    name=card_name,
                    numbers=numbers,
                    is_default=is_default
                )
                
                created_cards += 1
                self.stdout.write(f"  ✓ Created: {card_name} (Default: {is_default})")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_cards} custom bingo cards!")
        )
