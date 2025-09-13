from django.db import models
from users.models import User

class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.entry_fee}"

class PlayerGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    has_bingo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.game.entry_fee}"

class Winner(models.Model):
    player = models.ForeignKey(PlayerGame, on_delete=models.CASCADE)
    prize = models.DecimalField(max_digits=10, decimal_places=2)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} - {self.prize}"



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
    
