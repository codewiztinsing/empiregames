from django.shortcuts import render
from .models import Game
def index(request):
    return render(request, 'game/index.html')


def game_details(request, game_id):
    game = Game.objects.get(id=game_id)
    context = {
        'game': game
    }
    return render(request, 'dashboard/game_details.html', context)
