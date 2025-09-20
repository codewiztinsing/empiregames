from django.db import models
from users.models import User
from decimal import Decimal


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='waiting')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    players = models.JSONField(default=list)
    ended = models.BooleanField(default=False)
    ended_at = models.DateTimeField(null=True, blank=True)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_players = models.IntegerField(default=0)
    total_win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    game_duration = models.DurationField(null=True, blank=True)
    room_name = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self):
        return f"Game #{self.id} - Room {self.entry_fee} ETB"
    
    def save(self, *args, **kwargs):
        # Set room name based on entry fee
        if not self.room_name and self.entry_fee:
            self.room_name = f"Room {self.entry_fee} ETB"
        
        # Set started_at when game starts
        if self.started and not self.started_at:
            from django.utils import timezone
            self.started_at = timezone.now()
        
        # Set ended_at when game ends
        if self.ended and not self.ended_at:
            from django.utils import timezone
            self.ended_at = timezone.now()
            
            # Calculate game duration
            if self.started_at:
                self.game_duration = self.ended_at - self.started_at
        
        super().save(*args, **kwargs)
    
    @property
    def player_count(self):
        """Get the actual number of players from PlayerGame"""
        return self.playergame_set.count()
    
    @property
    def is_active(self):
        """Check if game is currently active"""
        return self.status == 'in_progress' and not self.ended
    
    @property
    def can_join(self):
        """Check if players can still join this game"""
        return self.status == 'waiting' and not self.ended
    
    @property
    def prize_pool(self):
        """Calculate total prize pool"""
        from decimal import Decimal
        return Decimal(str(self.player_count)) * self.entry_fee
    
    @property
    def commission_amount(self):
        """Calculate commission amount"""
        from decimal import Decimal
        return self.prize_pool * Decimal('0.1')  # 10% commission
    
    @property
    def winner_payout(self):
        """Calculate winner payout"""
        return self.prize_pool - self.commission_amount

class PlayerGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='playergame_set')
    has_bingo = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    boards_count = models.IntegerField(default=1)
    total_bet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_winner = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-joined_at']
        verbose_name = "Player Game"
        verbose_name_plural = "Player Games"
        unique_together = ['user', 'game']

    def __str__(self):
        return f"{self.user.username} - Game #{self.game.id} - {self.game.entry_fee} ETB"
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        
        # Calculate total bet based on boards count and entry fee
        if self.game and self.boards_count:
            self.total_bet = Decimal(str(self.boards_count)) * self.game.entry_fee
        
        # Set is_winner if has_bingo
        if self.has_bingo:
            self.is_winner = True
            # Set win amount to the winner payout
            if self.game:
                self.win_amount = self.game.winner_payout
        
        super().save(*args, **kwargs)



class GameSettings(models.Model):
    game_speed = models.IntegerField()
    count_down_time = models.IntegerField()
    def __str__(self):
        return f"{self.game_speed} - {self.count_down_time}"


class GameType(models.Model):
    bet_amount = models.IntegerField(default=10)
    commission = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.bet_amount}"
    
