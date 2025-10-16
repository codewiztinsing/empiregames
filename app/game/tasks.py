import logging
from celery import shared_task
from game.models import Game
from wallet.models import Transaction,Wallet
from users.models import User
from users.referral_services import ReferralService
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
    logger.info(f"Players = {players}")
    charged_players = []
    for player in players:
        try:
            player_obj = get_object_or_404(User, telegram_id=player)
            logger.info(f"Player: {player_obj}")
            
            
            wallet = Wallet.objects.get(user=player_obj)
            logger.info(f"Wallet balance: {wallet.balance}")

            # check transcation and deduct the amount from the wallet 
            existing_transaction = Transaction.objects.filter(reference=game_id,type="BET",user = player_obj).first()
            if existing_transaction:
                logger.info("Transaction already exists")
                continue
            else:
                wallet.balance -= (float(entry_fee) * players[player])
                wallet.save()
                logger.info(f"Wallet balance after deduction: {wallet.balance}")
                # push transaction
                push_transaction(player_obj.telegram_id, entry_fee,entry_fee * players[player],"BET","success",game_id)
            charged_players.append(player_obj.id)
            logger.info(f"Charged players: {charged_players}")
          
            
        except Exception as e:
            logger.error(f"Error charging player {player}: {e}")
    return charged_players
    



@shared_task
def update_player_balance(player_id,win_amount,game_id):
    player = get_object_or_404(User,telegram_id=player_id)
    wallet = get_object_or_404(Wallet,user = player)
    game = get_object_or_404(Game,id=game_id)

    existing_transaction = Transaction.objects.filter(reference=game_id,type="WIN",user = player).first()
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
        
        # Process referral bonuses
        try:
            ReferralService.process_win_bonus(player, float(win_amount), str(game_id))
            logger.info(f"Processed referral bonuses for player {player_id}")
        except Exception as e:
            logger.error(f"Error processing referral bonuses: {e}")
        
      
        
        return True,wallet.balance


"""PlayerGame removed: create_player_games task no longer needed."""


@shared_task
def process_tuesday_bonus_payments():
    """Process bonus payments every Tuesday"""
    logger.info("Processing Tuesday bonus payments")
    try:
        success, message = ReferralService.process_tuesday_bonus_payments()
        logger.info(f"Tuesday bonus processing result: {message}")
        return success
    except Exception as e:
        logger.error(f"Error processing Tuesday bonuses: {e}")
        return False