import logging
from celery import shared_task
from game.models import Game, FakePlayerSettings
from wallet.models import Transaction,Wallet
from users.models import User
# Referral services removed
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

  

@shared_task
def push_transaction(player_id, entry_fee, amount, transaction_type, status, reference):
    logger.info(f"=== PUSH_TRANSACTION TASK STARTED ===")
    logger.info(f"Task ID: {push_transaction.request.id}")
    logger.info(f"Player ID: {player_id} (type: {type(player_id)})")
    logger.info(f"Entry fee: {entry_fee} (type: {type(entry_fee)})")
    logger.info(f"Amount: {amount} (type: {type(amount)})")
    logger.info(f"Transaction type: {transaction_type}")
    logger.info(f"Status: {status}")
    logger.info(f"Reference: {reference} (type: {type(reference)})")
    
    try:
        # Convert player_id to string for lookup
        player_id_str = str(player_id)
        logger.info(f"Looking for user with telegram_id: {player_id_str}")
        
        player = get_object_or_404(User, telegram_id=player_id_str)
        logger.info(f"Found player: {player.id} (username: {player.username})")
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=player,
            amount=amount,
            type=transaction_type,
            status=status,
            reference=str(reference)
        )
        logger.info(f"Created transaction: {transaction.id}")
        logger.info(f"Transaction details: user={transaction.user.id}, amount={transaction.amount}, type={transaction.type}, status={transaction.status}, reference={transaction.reference}")
        
        logger.info(f"=== PUSH_TRANSACTION TASK COMPLETED ===")
        return transaction
        
    except Exception as e:
        logger.error(f"Error in push_transaction: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@shared_task
def charge_player(players, entry_fee, game_id):
    logger.info(f"=== CHARGE_PLAYER TASK STARTED ===")
    logger.info(f"Task ID: {charge_player.request.id}")
    logger.info(f"Players data type: {type(players)}")
    logger.info(f"Players data: {players}")
    logger.info(f"Entry fee: {entry_fee} (type: {type(entry_fee)})")
    logger.info(f"Game ID: {game_id} (type: {type(game_id)})")
    
    charged_players = []
    
    # Handle different data structures
    if isinstance(players, list):
        logger.info("Players is a list, converting to dict format")
        players_dict = {}
        for player_data in players:
            if hasattr(player_data, 'playerId') and hasattr(player_data, 'numberOfBoards'):
                # It's a PlayerSchema object
                players_dict[player_data.playerId] = player_data.numberOfBoards
                logger.info(f"Converted player {player_data.playerId} with {player_data.numberOfBoards} boards")
            elif isinstance(player_data, dict):
                # It's a dictionary
                players_dict[player_data.get('playerId')] = player_data.get('numberOfBoards', 1)
                logger.info(f"Converted player {player_data.get('playerId')} with {player_data.get('numberOfBoards', 1)} boards")
        players = players_dict
        logger.info(f"Converted players dict: {players}")
    elif isinstance(players, dict):
        logger.info("Players is already a dict")
    else:
        logger.error(f"Unexpected players data type: {type(players)}")
        return charged_players
    
    logger.info(f"Processing {len(players)} players")
    
    for player_id, number_of_boards in players.items():
        try:
            logger.info(f"=== PROCESSING PLAYER {player_id} ===")
            logger.info(f"Number of boards: {number_of_boards}")
            
            # Convert player_id to string if it's not already
            player_id_str = str(player_id)
            logger.info(f"Looking for user with telegram_id: {player_id_str}")
            
            player_obj = get_object_or_404(User, telegram_id=player_id_str)
            logger.info(f"Found player: {player_obj.id} (username: {player_obj.username})")
            
            # Get or create wallet
            wallet, created = Wallet.objects.get_or_create(user=player_obj)
            if created:
                logger.info(f"Created new wallet for player {player_obj.id}")
            logger.info(f"Wallet balance before: {wallet.balance}")
            
            # Calculate charge amount
            charge_amount = float(entry_fee) * number_of_boards
            logger.info(f"Charge amount: {charge_amount} (entry_fee: {entry_fee} * boards: {number_of_boards})")
            
            # Check for existing transaction
            existing_transaction = Transaction.objects.filter(
                reference=str(game_id),
                type="BET",
                user=player_obj
            ).first()
            
            if existing_transaction:
                logger.info(f"Transaction already exists for player {player_id}, skipping")
                logger.info(f"Existing transaction: {existing_transaction.id}")
                continue
            
            # Check if player has sufficient balance
            if wallet.balance < charge_amount:
                logger.warning(f"Insufficient balance for player {player_id}: {wallet.balance} < {charge_amount}")
                continue
            
            # Deduct amount from wallet
            wallet.balance -= charge_amount
            wallet.save()
            logger.info(f"Wallet balance after deduction: {wallet.balance}")
            
            # Create transaction record
            transaction = push_transaction(
                player_obj.telegram_id, 
                entry_fee, 
                charge_amount, 
                "BET", 
                "success", 
                str(game_id)
            )
            logger.info(f"Created transaction: {transaction}")
            
            charged_players.append(player_obj.id)
            logger.info(f"Successfully charged player {player_id}")
            
        except Exception as e:
            logger.error(f"Error charging player {player_id}: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info(f"=== CHARGE_PLAYER TASK COMPLETED ===")
    logger.info(f"Successfully charged {len(charged_players)} players: {charged_players}")
    return charged_players
    



@shared_task
def update_player_balance(player_id, win_amount, game_id):
    logger.info(f"=== UPDATE_PLAYER_BALANCE TASK STARTED ===")
    logger.info(f"Task ID: {update_player_balance.request.id}")
    logger.info(f"Player ID: {player_id} (type: {type(player_id)})")
    logger.info(f"Win amount: {win_amount} (type: {type(win_amount)})")
    logger.info(f"Game ID: {game_id} (type: {type(game_id)})")
    
    try:
        # Convert player_id to string for lookup
        player_id_str = str(player_id)
        logger.info(f"Looking for user with telegram_id: {player_id_str}")
        
        player = get_object_or_404(User, telegram_id=player_id_str)
        logger.info(f"Found player: {player.id} (username: {player.username})")
        
        wallet = get_object_or_404(Wallet, user=player)
        logger.info(f"Wallet balance before win: {wallet.balance}")
        
        game = get_object_or_404(Game, id=game_id)
        logger.info(f"Found game: {game.id} (status: {game.status})")

        existing_transaction = Transaction.objects.filter(
            reference=str(game_id),
            type="WIN",
            user=player
        ).first()
        
        if existing_transaction:
            logger.info(f"WIN transaction already exists for player {player_id}, skipping")
            logger.info(f"Existing transaction: {existing_transaction.id}")
            return False, wallet.balance
        else:
            logger.info(f"Adding {win_amount} to player balance")
            wallet.balance += float(win_amount)
            wallet.save()
            logger.info(f"Wallet balance after win: {wallet.balance}")
            
            # Update game status
            game.status = 'completed'
            game.ended_at = timezone.now()
            game.save()
            logger.info(f"Updated game {game_id} status to completed")
            
            # Create transaction record
            transaction = push_transaction(
                player.telegram_id, 
                win_amount, 
                win_amount, 
                "WIN", 
                "success", 
                str(game_id)
            )
            logger.info(f"Created WIN transaction: {transaction}")
            
            # Referral bonuses removed
            
            logger.info(f"=== UPDATE_PLAYER_BALANCE TASK COMPLETED ===")
            return True, wallet.balance
            
    except Exception as e:
        logger.error(f"Error in update_player_balance: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise






  


@shared_task
def activate_fake_players():
    logger.info("Activating fake players")
    try:
        fake_player_settings = FakePlayerSettings.get_solo()
        fake_player_settings.fake_players_can_win = True
        fake_player_settings.save()
        return True
    except Exception as e:
        logger.error(f"Error activating fake players: {e}")
        return False
   

@shared_task
def deactivate_fake_players():
    logger.info("Deactivating fake players")
    try:
        fake_player_settings = FakePlayerSettings.get_solo()
        fake_player_settings.fake_players_can_win = False
        fake_player_settings.max_fake_players = 50
        fake_player_settings.save()
        return True
    except Exception as e:
        logger.error(f"Error deactivating fake players: {e}")
        return False