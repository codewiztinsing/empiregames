from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.utils import timezone
from .models import Game, PlayerGame, GameType
from users.models import User

def index(request):
    """Game index page"""
    return render(request, 'game/index.html')

def game_details(request, game_id):
    """Enhanced game details view with comprehensive information"""
    game = get_object_or_404(Game.objects.select_related('winner'), id=game_id)
    
    # Get all players in this game with their details
    player_games = PlayerGame.objects.filter(game=game).select_related('user').order_by('-joined_at')
    
    # Calculate game statistics
    total_players = player_games.count()
    total_bet_amount = player_games.aggregate(Sum('total_bet'))['total_bet__sum'] or 0
    total_boards = player_games.aggregate(Sum('boards_count'))['boards_count__sum'] or 0
    winners = player_games.filter(has_bingo=True)
    winner_count = winners.count()
    
    # Get game type information
    game_type = GameType.objects.filter(bet_amount=game.entry_fee).first()
    
    # Recent games of same type
    recent_similar_games = Game.objects.filter(
        entry_fee=game.entry_fee
    ).exclude(id=game.id).order_by('-created_at')[:5]
    
    # Player statistics for this game
    player_stats = []
    for player_game in player_games:
        user = player_game.user
        # Get user's overall game statistics
        user_total_games = PlayerGame.objects.filter(user=user).count()
        user_wins = PlayerGame.objects.filter(user=user, has_bingo=True).count()
        user_win_rate = (user_wins / user_total_games * 100) if user_total_games > 0 else 0
        
        player_stats.append({
            'player_game': player_game,
            'user': user,
            'total_games': user_total_games,
            'wins': user_wins,
            'win_rate': round(user_win_rate, 2),
        })
    
    context = {
        'game': game,
        'player_games': player_games,
        'total_players': total_players,
        'total_bet_amount': total_bet_amount,
        'total_boards': total_boards,
        'winner_count': winner_count,
        'game_type': game_type,
        'recent_similar_games': recent_similar_games,
        'player_stats': player_stats,
    }
    return render(request, 'dashboard/game_details.html', context)
