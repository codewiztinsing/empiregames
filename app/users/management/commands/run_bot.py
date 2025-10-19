import os
import sys
import django
import logging
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import the bot module
from webbot import main

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode',
        )

    def handle(self, *args, **options):
        if options['debug']:
            logging.basicConfig(level=logging.DEBUG)
            self.stdout.write(
                self.style.SUCCESS('Debug mode enabled')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Starting Telegram bot...')
        )
        
        try:
            # Run the bot
            main()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Bot stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Bot error: {e}')
            )
            logger.error(f'Bot error: {e}', exc_info=True)
