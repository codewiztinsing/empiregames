import logging
from celery import shared_task
from game.models import PlayerGame,Game
from wallet.models import Transaction,Wallet
from users.models import User
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

  

@shared_task
def push_transaction(player_id, entry_fee,amount,type,status,reference):
    logger.info(f"Push transaction: {player_id}, {entry_fee}, {amount}, {type}, {status}, {reference}")
    player = get_object_or_404(User,telegram_id=player_id)
    logger.info(f"Player: {player.id}")
    transaction = Transaction.objects.create(
        user=player,
        amount=amount,
        type=type,
        status=status,
        reference=reference
    )
    return transaction


@shared_task
def charge_player(players, entry_fee, game_id):
    logger.info(f"Charge player: {players}, {entry_fee}, {game_id}")
    logger.info(f"Players = ",players)
    charged_players = []
    for player in players:
        player = get_object_or_404(User,telegram_id=player)
        logger.info("Player ",player)
        wallet = get_object_or_404(Wallet,user = player)
        existing_transaction = Transaction.objects.filter(reference=game_id,type="BET").first()
        if existing_transaction:
            logger.info("Transaction already exists")
            continue
        else:
            wallet.balance -= float(entry_fee)
            push_transaction(player.telegram_id, entry_fee,entry_fee,"BET","success",game_id)
            charged_players.append(player.id)
            wallet.save()
            logger.info("Wallet balance ",wallet.balance)
    return charged_players
    



@shared_task
def update_player_balance(player_id,win_amount,game_id):
    logger.info(f"Update player balance: {player_id}")
    player = get_object_or_404(User,telegram_id=player_id)
    logger.info("Player ",player.id)
    wallet = get_object_or_404(Wallet,user = player)
    logger.info("Wallet ",wallet)
    game = get_object_or_404(Game,id=game_id)
    logger.info("Game ",game)
    existing_transaction = Transaction.objects.filter(reference=game_id,type="WIN").first()
    if existing_transaction:
        logger.info("Transaction already exists")
        return False,wallet.balance
    else:
        wallet.balance += float(win_amount)
        game.ended = True
        game.started = True
        game.save()
    
        push_transaction(player.telegram_id, win_amount,win_amount,"WIN","success",game_id)
        wallet.save()
        return True,wallet.balance