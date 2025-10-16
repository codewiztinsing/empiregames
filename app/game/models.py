from django.db import models
from users.models import User

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='waiting')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    players = models.JSONField(default=list)
    ended = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ended_at = models.DateTimeField(blank=True, null=True)
    game_duration = models.DurationField(blank=True, null=True)
    room_name = models.CharField(max_length=50, blank=True, null=True)
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
    
