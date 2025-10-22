from django.shortcuts import render
from users.models import User
from wallet.models import Wallet, Transaction
from game.models import Game
from django.db.models import Sum





def dashboard(request):
    user = User.objects.all()
    wallet = {
        "total_balance": Wallet.objects.aggregate(Sum('balance'))['balance__sum'],
        "total_withdrawals": Transaction.objects.filter(type='WITHDRAW').aggregate(Sum('amount'))['amount__sum'],
        "total_deposits": Transaction.objects.filter(type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'],
    }
    print(wallet)
    game = Game.objects.all()
    context = {
        'user': user,
        'wallet': wallet,   
        'page_title': 'Dashboard Overview',
        'games_played': game.count(),
        'games_won': game.filter(ended_at__isnull=False).count(),
        'win_rate': (game.filter(ended_at__isnull=False).count() / game.count()) * 100 if game.count() > 0 else 0,
        'current_streak': 0,
        'best_streak': 0,
        'recent_activities': [],
        'statistics': {
            'total_games': game.count(),
            'wins': game.filter(ended_at__isnull=False).count(),
            'losses': game.filter(ended_at__isnull=True).count(),
            'draws': 0,  # No draws in bingo games
        }
    }
    return render(request, 'dashboard/index.html',context)

def custom_404(request, exception):
    print("404 error")
    return render(request, '404.html', status=404)


def custom_500(request):
    print("500 error")
    return render(request, '500.html', status=500)