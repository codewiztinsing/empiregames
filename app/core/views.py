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
        'games_won': game.filter(ended=True).count(),
        'win_rate': (game.filter(ended=True).count() / game.count()) * 100,
        'current_streak': 0,
        'best_streak': 0,
        'recent_activities': [],
        'statistics': {
            'total_games': game.count(),
            'wins': game.filter(ended=True).count(),
            'losses': game.filter(ended=False).count(),
            'draws': game.filter(ended=None).count(),
        }
    }
    return render(request, 'dashboard/index.html',context)

def custom_404(request, exception):
    print("404 error")
    return render(request, '404.html', status=404)


def custom_500(request):
    print("500 error")
    return render(request, '500.html', status=500)