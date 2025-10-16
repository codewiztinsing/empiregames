from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with phone and telegram_id'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--phone', type=str, help='Phone number')
        parser.add_argument('--telegram_id', type=str, help='Telegram ID')
        parser.add_argument('--password', type=str, help='Password (for non-interactive mode)')
        parser.add_argument('--noinput', action='store_true', help='Non-interactive mode')

    def handle(self, *args, **options):
        if options['noinput']:
            username = options['username']
            phone = options['phone']
            telegram_id = options['telegram_id']
            password = options['password']
            
            if not all([username, phone, telegram_id, password]):
                self.stdout.write(
                    self.style.ERROR('Error: --username, --phone, --telegram_id, and --password are required in non-interactive mode')
                )
                return
        else:
            # Interactive mode
            username = input('Username: ')
            phone = input('Phone number: ')
            telegram_id = input('Telegram ID: ')
            
            # Get password
            password = getpass.getpass('Password: ')
            password_confirm = getpass.getpass('Password (again): ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Error: Passwords do not match'))
                return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'Error: Username "{username}" already exists'))
            return
        
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.ERROR(f'Error: Phone "{phone}" already exists'))
            return
            
        if User.objects.filter(telegram_id=telegram_id).exists():
            self.stdout.write(self.style.ERROR(f'Error: Telegram ID "{telegram_id}" already exists'))
            return

        try:
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                phone=phone,
                telegram_id=telegram_id,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
