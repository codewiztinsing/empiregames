import logging
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import transaction

from game.models import PlayerGame, Game
from wallet.models import Transaction, Wallet
from users.models import User, ReferralBonus
from users.referral_services import ReferralService

logger = logging.getLogger(__name__)

# -------------------------------
# Transaction push task
# -------------------------------
@shared_task(queue='payments')
def push_transaction(player_id, amount, actual_amount, type, status, reference):
    """
    Create a transaction record for the player.
    """
    try:
        player = get_object_or_404(User, telegram_id=player_id)
        transaction_record = Transaction.objects.create(
            user=player,
            amount=actual_amount,
            type=type,
            status=status,
            reference=reference
        )
        logger.info(f"Transaction pushed: {transaction_record}")
        return transaction_record.id
    except Exception as e:
        logger.error(f"Failed to push transaction for player {player_id}: {e}")
        return None

# -------------------------------
# Charge players for a game
# -------------------------------
@shared_task(queue='payments')
def charge_player(players_dict, entry_fee, game_id):
    """
    Charge multiple players for a game using wallet first, then referral bonuses.
    players_dict = {telegram_id: number_of_boards}
    """
    logger.info(f"Charging players for game {game_id}: {players_dict}")
    charged_players = []

    for player_id, number_of_boards in players_dict.items():
        try:
            player = get_object_or_404(User, telegram_id=player_id)
            wallet = Wallet.objects.get(user=player)

            total_required = float(entry_fee) * number_of_boards

            # Skip if BET transaction already exists
            if Transaction.objects.filter(reference=game_id, type="BET", user=player).exists():
                logger.info(f"BET transaction already exists for player {player_id}")
                continue

            with transaction.atomic():
                # -----------------------
                # Step 1: Deduct from wallet
                # -----------------------
                wallet_amount = min(wallet.balance, total_required)
                wallet.balance -= wallet_amount
                wallet.save()
                if wallet_amount > 0:
                    push_transaction.delay(player.telegram_id, wallet_amount, wallet_amount, "BET", "success", game_id)

                remaining_required = total_required - wallet_amount

                # -----------------------
                # Step 2: Deduct only needed referral bonuses
                # -----------------------
                if remaining_required > 0:
                    referral_bonuses = ReferralBonus.objects.filter(referrer=player, status="approved").order_by("id")
                    used_bonus = 0

                    for bonus in referral_bonuses:
                        if used_bonus >= remaining_required:
                            break
                        take_amount = min(bonus.bonus_amount, remaining_required - used_bonus)
                        used_bonus += take_amount

                        if take_amount == bonus.bonus_amount:
                            # Full bonus used, delete it
                            bonus.delete()
                        else:
                            # Partial bonus used, reduce its amount
                            bonus.bonus_amount -= take_amount
                            bonus.save()

                    if used_bonus > 0:
                        # Add used referral bonus to wallet to allow bet deduction
                        wallet.balance += used_bonus
                        wallet.save()
                        push_transaction.delay(player.telegram_id, used_bonus, used_bonus, "REFERRAL_BONUS", "success", game_id)

                        # Deduct the remaining amount now
                        wallet.balance -= remaining_required
                        wallet.save()
                        push_transaction.delay(player.telegram_id, remaining_required, remaining_required, "BET", "success", game_id)

                charged_players.append(player.id)
                logger.info(f"Successfully charged player {player_id}")

        except Exception as e:
            logger.error(f"Error charging player {player_id}: {e}")

    logger.info(f"All charged players: {charged_players}")
    return charged_players

# -------------------------------
# Update player balance for wins
# -------------------------------
@shared_task(queue='payments')
def update_player_balance(player_id, win_amount, game_id):
    try:
        player = get_object_or_404(User, telegram_id=player_id)
        wallet = get_object_or_404(Wallet, user=player)
        game = get_object_or_404(Game, id=game_id)

        if Transaction.objects.filter(reference=game_id, type="WIN", user=player).exists():
            logger.info(f"WIN transaction already exists for player {player_id}")
            return False, wallet.balance

        with transaction.atomic():
            wallet.balance += float(win_amount)
            wallet.save()
            push_transaction.delay(player.telegram_id, win_amount, win_amount, "WIN", "success", game_id)

            game.ended = True
            game.started = False
            game.save()

            # Process referral win bonuses
            try:
                ReferralService.process_win_bonus(player, float(win_amount), str(game_id))
                logger.info(f"Processed referral bonuses for player {player_id}")
            except Exception as e:
                logger.error(f"Error processing referral bonuses: {e}")

        return True, wallet.balance

    except Exception as e:
        logger.error(f"Error updating player balance {player_id}: {e}")
        return False, 0

# -------------------------------
# Create PlayerGame records
# -------------------------------
@shared_task(queue='payments')
def create_player_games(game_id, players_dict):
    """
    Create PlayerGame records for all players in a game.
    players_dict = {telegram_id: number_of_boards}
    """
    logger.info(f"Creating PlayerGame records for game {game_id}")
    try:
        game = get_object_or_404(Game, id=game_id)
        with transaction.atomic():
            for player_id, boards_count in players_dict.items():
                try:
                    player = get_object_or_404(User, telegram_id=player_id)
                    player_game, created = PlayerGame.objects.get_or_create(
                        user=player,
                        game=game,
                        defaults={
                            'boards_count': boards_count,
                            'total_bet': float(game.entry_fee) * boards_count
                        }
                    )
                    if created:
                        logger.info(f"Created PlayerGame for player {player_id}")
                    else:
                        logger.info(f"PlayerGame already exists for player {player_id}")
                except Exception as e:
                    logger.error(f"Error creating PlayerGame for player {player_id}: {e}")
        return True
    except Exception as e:
        logger.error(f"Error in create_player_games: {e}")
        return False

# -------------------------------
# Process weekly bonus payments
# -------------------------------
@shared_task(queue='payments')
def process_tuesday_bonus_payments():
    """
    Process bonus payments every Tuesday
    """
    logger.info("Processing Tuesday bonus payments")
    try:
        success, message = ReferralService.process_tuesday_bonus_payments()
        logger.info(f"Tuesday bonus processing result: {message}")
        return success
    except Exception as e:
        logger.error(f"Error processing Tuesday bonuses: {e}")
        return False












# import logging
# from celery import shared_task
# from game.models import PlayerGame,Game
# from wallet.models import Transaction,Wallet
# from users.models import User
# from users.referral_services import ReferralService
# from django.shortcuts import get_object_or_404
# from django.db.models import Sum
# from users.models import ReferralBonus
# logger = logging.getLogger(__name__)

  

# @shared_task(queue='payments')
# def push_transaction(player_id, entry_fee,amount,type,status,reference):
#     logger.info(f"Push transaction: {player_id}, {entry_fee}, {amount}, {type}, {status}, {reference}")
#     player = get_object_or_404(User,telegram_id=player_id)
#     logger.info(f"Player: {player.id}")
#     transaction = Transaction.objects.create(
#         user=player,
#         amount=amount,
#         type=type,
#         status=status,
#         reference=reference
#     )
#     return transaction


# @shared_task(queue='payments')
# def charge_player(players, entry_fee, game_id):
#     logger.info(f"Charge player: {players}, {entry_fee}, {game_id}")
#     logger.info(f"Players = {players}")
#     charged_players = []
#     for player in players:
#         try:
#             player_obj = get_object_or_404(User, telegram_id=player)
#             logger.info(f"Player: {player_obj}")
            
            
#             wallet = Wallet.objects.get(user=player_obj)
#             logger.info(f"Wallet balance: {wallet.balance}")

#             # check transcation and deduct the amount from the wallet 
#             existing_transaction = Transaction.objects.filter(reference=game_id,type="BET",user = player_obj).first()
#             if existing_transaction:
#                 logger.info("Transaction already exists")
#                 continue
#             else:
#                 required_amount = float(entry_fee) * players[player]
#                 original_wallet_balance = wallet.balance

#                 # First, try to use the wallet balance ONLY, if it's enough
#                 if wallet.balance >= required_amount:
#                     wallet.balance -= required_amount
#                     wallet.save()
#                     logger.info(f"Wallet balance after deduction: {wallet.balance}")
#                     push_transaction(player_obj.telegram_id, entry_fee, required_amount, "BET", "success", game_id)

#                 else:
#                     # Not enough, so use wallet + referral bonus
#                     # Get available referral bonuses (approved) ordered by created (oldest first)
#                     referral_bonuses = ReferralBonus.objects.filter(referrer=player_obj, status="approved").order_by("id")
#                     total_referral = sum(bonus.bonus_amount for bonus in referral_bonuses)
                    
#                     amount_needed_from_bonuses = required_amount - wallet.balance
#                     if (wallet.balance + total_referral) < required_amount:
#                         logger.error(f"Player {player_obj.id} does not have enough funds (wallet + referral bonus).")
#                         continue  # Skip charging this player due to insufficient funds
                    
#                     # Use wallet balance first (down to zero), then referralbonus
#                     amount_from_wallet = wallet.balance
#                     if wallet.balance > 0:
#                         wallet.balance = 0
#                         wallet.save()
#                         if amount_from_wallet > 0:
#                             push_transaction(player_obj.telegram_id, entry_fee, amount_from_wallet, "BET", "success", game_id)
                    
#                     # Now, cover the rest from referral bonuses by deleting, as instructed
#                     used_bonuses_amount = 0.0
#                     bonuses_to_delete = []
#                     for bonus in referral_bonuses:
#                         if used_bonuses_amount >= amount_needed_from_bonuses:
#                             break
#                         take_amount = min(bonus.bonus_amount, amount_needed_from_bonuses - used_bonuses_amount)
#                         used_bonuses_amount += take_amount
#                         bonuses_to_delete.append(bonus.id)
                    
#                     # Delete the bonuses that were used
#                     if bonuses_to_delete:
#                         ReferralBonus.objects.filter(id__in=bonuses_to_delete).delete()
#                         # Optionally, push a transaction for the referral bonus deduction
#                         push_transaction(player_obj.telegram_id, used_bonuses_amount, used_bonuses_amount, "REFERRAL_BONUS", "success", game_id)
#                 # get total refferal bonus from users.RefferalBonus
#                 refferal_bonus = ReferralBonus.objects.filter(referrer=player_obj,status="approved").aggregate(total=Sum("bonus_amount"))["total"] or 0
#                 if refferal_bonus > 0:
#                     # deduct the refferal bonus from the wallet
#                     wallet.balance -= refferal_bonus
#                     wallet.save()
#                     logger.info(f"Wallet balance after deduction: {wallet.balance}")
#                     # push transaction
#                     push_transaction(player_obj.telegram_id, refferal_bonus,refferal_bonus,"REFERRAL_BONUS","success",game_id)
#                 else:
#                     logger.info(f"No refferal bonus found for player {player_obj.id}")
             
#                 if wallet.balance < (float(entry_fee) * players[player]):
#                     wallet.balance = 0
#                     wallet.save()
#                     logger.info(f"Wallet balance after deduction: {wallet.balance}")
#                     # push transaction
#                     push_transaction(player_obj.telegram_id, entry_fee,wallet.balance,"BET","success",game_id)
#                 else:
#                     wallet.balance -= (float(entry_fee) * players[player])
#                     wallet.save()
#                     logger.info(f"Wallet balance after deduction: {wallet.balance}")
#                     # push transaction
#                     push_transaction(player_obj.telegram_id, entry_fee,entry_fee * players[player],"BET","success",game_id)
#             charged_players.append(player_obj.id)
#             logger.info(f"Charged players: {charged_players}")
          
            
#         except Exception as e:
#             logger.error(f"Error charging player {player}: {e}")
#     return charged_players
    



# @shared_task(queue='payments')
# def update_player_balance(player_id,win_amount,game_id):
#     player = get_object_or_404(User,telegram_id=player_id)
#     wallet = get_object_or_404(Wallet,user = player)
#     game = get_object_or_404(Game,id=game_id)

#     existing_transaction = Transaction.objects.filter(reference=game_id,type="WIN",user = player).first()
#     if existing_transaction:
#         logger.info("Transaction already exists")
#         return False,wallet.balance
#     else:
#         wallet.balance += float(win_amount)
#         game.ended = True
#         game.started = True
#         game.save()
#         push_transaction(player.telegram_id, win_amount,win_amount,"WIN","success",game_id)
#         wallet.save()
        
#         # Process referral bonuses
#         try:
#             ReferralService.process_win_bonus(player, float(win_amount), str(game_id))
#             logger.info(f"Processed referral bonuses for player {player_id}")
#         except Exception as e:
#             logger.error(f"Error processing referral bonuses: {e}")
        
      
        
#         return True,wallet.balance


# @shared_task(queue='payments')
# def create_player_games(game_id, players_dict):
#     """
#     Create PlayerGame records for all players in a game
#     """
#     logger.info(f"Creating player games for game {game_id} with players {players_dict}")
#     try:
#         game = get_object_or_404(Game, id=game_id)
        
#         for player_id, number_of_boards in players_dict.items():
#             try:
#                 player = get_object_or_404(User, telegram_id=player_id)
#                 player_game, created = PlayerGame.objects.get_or_create(
#                     user=player,
#                     game=game,
#                     defaults={
#                         'boards_count': number_of_boards,
#                         'total_bet': float(game.entry_fee) * number_of_boards
#                     }
#                 )
#                 if created:
#                     logger.info(f"Created PlayerGame for player {player_id} in game {game_id}")
#                 else:
#                     logger.info(f"PlayerGame already exists for player {player_id} in game {game_id}")
#             except Exception as e:
#                 logger.error(f"Error creating PlayerGame for player {player_id}: {e}")
        
#         return True
#     except Exception as e:
#         logger.error(f"Error in create_player_games: {e}")
#         return False


# @shared_task
# def process_tuesday_bonus_payments():
#     """Process bonus payments every Tuesday"""
#     logger.info("Processing Tuesday bonus payments")
#     try:
#         success, message = ReferralService.process_tuesday_bonus_payments()
#         logger.info(f"Tuesday bonus processing result: {message}")
#         return success
#     except Exception as e:
#         logger.error(f"Error processing Tuesday bonuses: {e}")
#         return False