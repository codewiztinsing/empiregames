from django.shortcuts import render
from users.models import User
from game.models import Game
from wallet.models import Wallet,Transaction
from datetime import datetime

def custom_404(request, exception):
    print("404 error")
    return render(request, '404.html', status=404)


def custom_500(request):
    print("500 error")
    return render(request, '500.html', status=500)



def dashboard_view(request):
    total_players = User.objects.count()
    total_games = Game.objects.count()
    wallets = Wallet.objects.all()
    today_games = Game.objects.filter(created_at__date=datetime.now().date()).count()
    today_deposits = Transaction.objects.filter(created_at__date=datetime.now().date(),type="DEPOSIT").count()
    today_withdrawals = Transaction.objects.filter(created_at__date=datetime.now().date(),type="WITHDRAW").count()
    today_new_players = User.objects.filter(date_joined__date=datetime.now().date()).count()
  
    available_balance = sum([wallet.balance for wallet in wallets])

    


    context = {
        "total_players": total_players,
        "total_games": total_games,
        "available_balance": available_balance,
        "today_games": today_games,
        "today_deposits": today_deposits,
        "today_withdrawals": today_withdrawals,
        "today_new_players": today_new_players
    }

   
    
    return render(request, 'dashboard/index.html', context)