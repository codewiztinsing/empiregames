from django.db import models
from users.models import User

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)

class PlayerGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.JSONField()  # stores card numbers
    has_bingo = models.BooleanField(default=False)

class Winner(models.Model):
    player = models.ForeignKey(PlayerGame, on_delete=models.CASCADE)
    prize = models.DecimalField(max_digits=10, decimal_places=2)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} - {self.prize}"
