from ninja import Router
from .models import Game, PlayerGame
from users.models import User
from wallet.models import Wallet
from django.shortcuts import get_object_or_404

game_router = Router()

@game_router.post("/join")
def join_game(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    wallet = get_object_or_404(Wallet, user=user)
    
    game = Game.objects.filter(started=False).last()
    if not game:
        game = Game.objects.create(entry_fee=10.00)

    if wallet.balance < game.entry_fee:
        return {"error": "Insufficient balance"}

    wallet.balance -= game.entry_fee
    wallet.save()

    PlayerGame.objects.create(user=user, game=game, card={})  # generate card later
    return {"message": "Joined game", "game_id": game.id}
