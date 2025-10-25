from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from users.models import Agent
from wallet.models import Wallet
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test deposits for players under agent ID 1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--agent-id',
            type=int,
            default=1,
            help='Agent ID to create deposits for their players (default: 1)'
        )
        parser.add_argument(
            '--deposits-per-player',
            type=int,
            default=3,
            help='Number of deposits per player (default: 3)'
        )

    def handle(self, *args, **options):
        agent_id = options['agent_id']
        deposits_per_player = options['deposits_per_player']
        
        try:
            agent = Agent.objects.get(id=agent_id)
            self.stdout.write(f"Found agent: {agent.user.username} (ID: {agent_id})")
        except Agent.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Agent with ID {agent_id} does not exist')
            )
            return

        # Get all players referred by this agent
        players = User.objects.filter(referred_by=agent.user)
        
        if not players.exists():
            self.stdout.write(
                self.style.ERROR(f'No players found for agent {agent.user.username}')
            )
            return

        created_deposits = 0
        total_amount = Decimal('0')
        
        for player in players:
            self.stdout.write(f"Creating deposits for player: {player.username}")
            
            # Get or create wallet for player
            wallet, created = Wallet.objects.get_or_create(user=player)
            
            for i in range(deposits_per_player):
                # Generate random deposit amount (50-500 Birr)
                amount = Decimal(str(random.randint(50, 500)))
                
                # Update wallet balance
                wallet.balance += float(amount)
                wallet.save()
                
                created_deposits += 1
                total_amount += amount
                self.stdout.write(f"  Created deposit: {amount} Birr")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_deposits} test deposits for {players.count()} players under agent {agent.user.username}'
            )
        )
        
        self.stdout.write(f"Total deposits created: {created_deposits}")
        self.stdout.write(f"Total deposit amount: {total_amount} Birr")
