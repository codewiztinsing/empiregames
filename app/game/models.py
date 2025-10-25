from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class GameRoom(models.Model):
    """
    Game rooms for organizing games by entry fee and settings
    """
    ROOM_TYPES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
        ('tournament', 'Tournament'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    # tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='game_rooms')
    
    # Room details
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='standard')
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='ETB')
    
    # Room settings
    max_players = models.PositiveIntegerField(default=100)
    min_players = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    # Game settings
    countdown_duration = models.PositiveIntegerField(default=30)  # seconds
    game_speed = models.PositiveIntegerField(default=5000)  # milliseconds
    max_fake_players = models.PositiveIntegerField(default=50)
    fake_player_threshold = models.PositiveIntegerField(default=10)
    
    # Financial settings
    house_edge_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=22.00)
    prize_pool_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=78.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['entry_fee', 'name']
        verbose_name = 'Game Room'
        verbose_name_plural = 'Game Rooms'
        # unique_together = ['tenant', 'entry_fee', 'name']
        indexes = [
            # models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['entry_fee']),
            models.Index(fields=['room_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.entry_fee} {self.currency}"
    
    def soft_delete(self):
        """Soft delete the game room"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def calculate_prize_pool(self, total_players):
        """Calculate prize pool based on total players"""
        return (total_players * self.entry_fee * self.prize_pool_percentage) / 100


class Game(models.Model):
    """
    Enhanced Game model with better tracking and analytics
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('countdown', 'Countdown'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    # tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='games')
    room = models.ForeignKey(GameRoom, on_delete=models.PROTECT, related_name='games')
    
    # Game details
    game_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    
    # Players and participation
    total_players = models.PositiveIntegerField(default=0)
    real_players = models.PositiveIntegerField(default=0)
    fake_players = models.PositiveIntegerField(default=0)
    
    # Financial information
    total_entry_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    prize_pool = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    house_edge_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Winner information
    winner = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    winner_is_fake = models.BooleanField(default=False)
    winner_card_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Game timing
    countdown_started_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Game progression
    numbers_called = models.PositiveIntegerField(default=0)
    total_numbers_called = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        # unique_together = ['tenant', 'game_number']
        indexes = [
            # models.Index(fields=['tenant', 'status']),
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['winner', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Game #{self.game_number} - {self.room.name} - {self.get_status_display()}"
    
    def soft_delete(self):
        """Soft delete the game"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def start_countdown(self):
        """Start the countdown phase"""
        self.status = 'countdown'
        self.countdown_started_at = timezone.now()
        self.save()
    
    def start_game(self):
        """Start the game"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def end_game(self, winner=None, winner_is_fake=False, winner_card_number=None):
        """End the game with winner information"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.winner = winner
        self.winner_is_fake = winner_is_fake
        self.winner_card_number = winner_card_number
        
        if self.started_at:
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
        
        self.save()
    
    def calculate_duration(self):
        """Calculate game duration"""
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        return None
    
    def get_winner_display(self):
        """Return a human-readable winner display"""
        if self.winner:
            return f"{self.winner.username} ({self.winner.telegram_id})"
        elif self.status == 'completed' and not self.winner:
            return "Fake Player"
        else:
            return "No Winner"


class PlayerGame(models.Model):
    """
    Track individual player participation in games
    """
    id = models.BigAutoField(primary_key=True)
    # tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='player_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_games')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='player_games')
    
    # Card information
    card_number = models.PositiveIntegerField()
    card_data = models.JSONField()  # Store the actual bingo card data
    
    # Participation details
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Game results
    is_winner = models.BooleanField(default=False)
    win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    numbers_matched = models.PositiveIntegerField(default=0)
    
    # Transaction reference
    bet_transaction = models.ForeignKey('finance.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='bet_player_games')
    win_transaction = models.ForeignKey('finance.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='win_player_games')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-joined_at']
        verbose_name = 'Player Game'
        verbose_name_plural = 'Player Games'
        unique_together = ['game', 'user']
        indexes = [
            # models.Index(fields=['tenant', 'user', 'created_at']),
            models.Index(fields=['game', 'is_winner']),
            models.Index(fields=['user', 'is_winner']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Game #{self.game.game_number} - Card #{self.card_number}"
    
    def mark_as_winner(self, win_amount):
        """Mark player as winner and set win amount"""
        self.is_winner = True
        self.win_amount = win_amount
        self.save()


class GameSettings(models.Model):
    """
    Tenant-specific game settings and configurations
    """
    # tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='game_settings')
    
    # Default game settings
    default_countdown_duration = models.PositiveIntegerField(default=30)
    default_game_speed = models.PositiveIntegerField(default=5000)
    default_house_edge = models.DecimalField(max_digits=5, decimal_places=2, default=22.00)
    
    # Fake player settings
    max_fake_players = models.PositiveIntegerField(default=50)
    fake_player_threshold = models.PositiveIntegerField(default=10)
    fake_players_can_win = models.BooleanField(default=True)
    fake_winner_probability = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    
    # Game limits
    max_games_per_day = models.PositiveIntegerField(default=1000)
    max_games_per_hour = models.PositiveIntegerField(default=100)
    min_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    max_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    
    # Custom settings
    custom_settings = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Game Settings'
        verbose_name_plural = 'Game Settings'
    
    def __str__(self):
        return f"Game Settings for {self.tenant.name}"


class FakePlayerSettings(models.Model):
    """
    Settings for fake player behavior (keeping existing functionality)
    """
    # tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='fake_player_settings')
    
    max_fake_players = models.PositiveIntegerField(default=50)
    calls_before_fake_winner = models.PositiveIntegerField(default=10)
    real_players_threshold = models.PositiveIntegerField(default=10)
    fake_players_can_win = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fake Player Settings'
        verbose_name_plural = 'Fake Player Settings'
        # unique_together = ['tenant']
    
    def __str__(self):
        return f"Fake Player Settings"
    
    @classmethod
    def get_solo(cls, tenant=None):
        """Get or create a single instance for the tenant"""
        if tenant:
            obj, created = cls.objects.get_or_create(tenant=tenant)
        else:
            # For backward compatibility, get the first one
            obj, created = cls.objects.get_or_create(pk=1)
        return obj


class CustomBingoCard(models.Model):
    """
    Custom bingo cards created by users
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='custom_bingo_cards')
    
    # Card details
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    # Card numbers stored as JSON
    numbers = models.JSONField(default=dict, help_text="Bingo card numbers organized by column (B, I, N, G, O)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'game_custom_bingo_card'
        verbose_name = 'Custom Bingo Card'
        verbose_name_plural = 'Custom Bingo Cards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def clean(self):
        """Validate the card numbers"""
        from django.core.exceptions import ValidationError
        
        if not isinstance(self.numbers, dict):
            raise ValidationError("Numbers must be a dictionary")
        
        # Check if all required columns are present
        required_columns = ['B', 'I', 'N', 'G', 'O']
        for column in required_columns:
            if column not in self.numbers:
                raise ValidationError(f"Missing column: {column}")
            
            if not isinstance(self.numbers[column], list) or len(self.numbers[column]) != 5:
                raise ValidationError(f"Column {column} must contain exactly 5 numbers")
        
        # Validate number ranges
        column_ranges = {
            'B': (1, 15),
            'I': (16, 30),
            'N': (31, 45),
            'G': (46, 60),
            'O': (61, 75)
        }
        
        all_numbers = []
        for column, numbers in self.numbers.items():
            min_val, max_val = column_ranges[column]
            for number in numbers:
                if not isinstance(number, int) or number < min_val or number > max_val:
                    raise ValidationError(f"Number {number} in column {column} is out of range ({min_val}-{max_val})")
                all_numbers.append(number)
        
        # Check for duplicates
        if len(all_numbers) != len(set(all_numbers)):
            raise ValidationError("Duplicate numbers found in the card")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_user_default_card(cls, user):
        """Get the user's default custom card"""
        return cls.objects.filter(user=user, is_default=True).first()
    
    @classmethod
    def get_user_cards(cls, user):
        """Get all custom cards for a user"""
        return cls.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    @classmethod
    def set_default_card(cls, user, card_id):
        """Set a card as default and unset others"""
        # Unset all other default cards for this user
        cls.objects.filter(user=user, is_default=True).update(is_default=False)
        
        # Set the specified card as default
        cls.objects.filter(user=user, id=card_id).update(is_default=True)
    
    def get_card_numbers(self):
        """Get formatted card numbers"""
        return {
            'B': self.numbers.get('B', []),
            'I': self.numbers.get('I', []),
            'N': self.numbers.get('N', []),
            'G': self.numbers.get('G', []),
            'O': self.numbers.get('O', [])
        }
    
