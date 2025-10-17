from django.db import models
from users.models import User

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='waiting')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    ended = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    started_at = models.DateTimeField(blank=True, null=True)
    total_players = models.IntegerField(default=0)
    real_players = models.IntegerField(default=0)
    fake_players = models.IntegerField(default=0)
    total_win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    def __str__(self):
        return f"{self.entry_fee}"
    
    def get_winner_display(self):
        """Return a human-readable winner display"""
        if self.winner:
            return f"{self.winner.username} ({self.winner.telegram_id})"
        elif self.status == 'completed' and not self.winner:
            return "Fake Player"
        else:
            return "No Winner"

"""
PlayerGame model removed per requirement to drop the table.
Make sure to create a migration to delete this model if it exists in DB.
"""
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


class FakePlayerSettings(models.Model):
    """Settings for fake player behavior in games"""
    max_fake_players = models.IntegerField(default=50, help_text="Maximum number of fake players")
    calls_before_fake_winner = models.IntegerField(default=10, help_text="Number of calls before fake winner can be activated")
    fake_players_can_win = models.BooleanField(default=True, help_text="Whether fake players can win games")
    real_players_threshold = models.IntegerField(default=10, help_text="Activate fake players if real players since last real-winner are below this")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fake Player Settings"
        verbose_name_plural = "Fake Player Settings"

    @classmethod
    def get_solo(cls):
        """Get or create the single instance of fake player settings"""
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Max: {self.max_fake_players}, Calls: {self.calls_before_fake_winner}, Can Win: {self.fake_players_can_win}"
    
