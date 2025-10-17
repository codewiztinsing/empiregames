from game.models import Game
from django.db.models import Sum




#
def count_real_players_in_games():
    # Find the last game where the winner was a real player (fake winners set winner=None)
    last_real_winner_game = (
        Game.objects.filter(winner__isnull=False)
        .order_by('-created_at')
        .first()
    )
    

    if not last_real_winner_game:
        return 0

    last_real_game_updated = last_real_winner_game.updated_at

    # Retrieve all games created after the last real winner game
    games_after_last_real = Game.objects.filter(created_at__gt=last_real_game_updated)

    # Count all real players in those games
    real_players = (
        games_after_last_real.aggregate(total_real_players=Sum('real_players'))
        .get('total_real_players')
    )

    return real_players or 0
