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
def update_player_balance(player_id, win_amount, game_id):
    logger.info(f"Update player balance: {player_id}, win_amount: {win_amount}, game_id: {game_id}")
    player = get_object_or_404(User, telegram_id=player_id)
    logger.info(f"Player: {player.id}")
    wallet = get_object_or_404(Wallet, user=player)
    logger.info(f"Wallet: {wallet}")
    game = get_object_or_404(Game, id=game_id)
    logger.info(f"Game: {game}")
    
    # Check if win transaction already exists
    existing_transaction = Transaction.objects.filter(reference=game_id, type="WIN", user=player).first()
    if existing_transaction:
        logger.info("Win transaction already exists")
        # Still update game status and winner even if transaction exists
    else:
        # Update wallet balance only if no existing transaction
        wallet.balance += float(win_amount)
        wallet.save()
        logger.info(f"Updated wallet balance: {wallet.balance}")
        
        # Create win transaction only if it doesn't exist
        push_transaction(player.telegram_id, win_amount, win_amount, "WIN", "success", game_id)
    
    # Always update game status and set winner
    game.ended = True
    game.started = False  # Game is now ended, so not started anymore
    game.status = "completed"
    game.winner = player  # Set the winner
    game.save()
    logger.info(f"Updated game status. Winner: {player.username}")
    
    # Update PlayerGame to mark as bingo/winner
    player_games = PlayerGame.objects.filter(game=game, user=player)
    for player_game in player_games:
        player_game.has_bingo = True
        player_game.save()
    logger.info(f"Updated {player_games.count()} PlayerGame entries to mark as bingo")
    
    return True, wallet.balance



@shared_task
def update_game_status(game_id, number_of_players, total_win_amount):
    """Update game status when game starts"""
    logger.info(f"Update game status: {game_id}")
    game = get_object_or_404(Game, id=game_id)
    logger.info("Game ", game)
    game.started = True
    game.status = "in_progress"
    game.total_players = number_of_players
    game.total_win_amount = total_win_amount
    game.save()
    return game


@shared_task
def end_game(game_id, winner_telegram_id=None):
    """End the game and optionally set winner"""
    logger.info(f"Ending game: {game_id}, winner: {winner_telegram_id}")
    game = get_object_or_404(Game, id=game_id)
    
    # Update game status to completed
    game.ended = True
    game.started = False
    game.status = "completed"
    
    # Set winner if provided
    if winner_telegram_id:
        try:
            winner = get_object_or_404(User, telegram_id=winner_telegram_id)
            game.winner = winner
            logger.info(f"Set winner: {winner.username}")
            
            # Update PlayerGame entries for the winner
            player_games = PlayerGame.objects.filter(game=game, user=winner)
            for player_game in player_games:
                player_game.has_bingo = True
                player_game.save()
            logger.info(f"Updated {player_games.count()} PlayerGame entries for winner")
            
        except Exception as e:
            logger.error(f"Error setting winner: {e}")
    
    # Calculate final game statistics
    player_games = PlayerGame.objects.filter(game=game)
    total_players = player_games.values('user').distinct().count()
    total_boards = sum(pg.boards_count or 0 for pg in player_games)
    total_bet_amount = sum(float(pg.total_bet or 0) for pg in player_games)
    
    game.total_players = total_players
    game.save()
    
    logger.info(f"Game ended successfully. Total players: {total_players}, Total boards: {total_boards}, Total bet: {total_bet_amount}")
    return {
        'game_id': game.id,
        'status': game.status,
        'winner': game.winner.username if game.winner else None,
        'total_players': total_players,
        'total_boards': total_boards,
        'total_bet_amount': total_bet_amount
    }


@shared_task
def create_player_games(game_id, players):
    logger.info(f"Create player games: {game_id}, players: {players}")
    game = get_object_or_404(Game, id=game_id)
    logger.info(f"Game: {game}")
    
    created_player_games = []
    for player_telegram_id, number_of_boards in players.items():
        try:
            # Get user by telegram_id
            user = get_object_or_404(User, telegram_id=player_telegram_id)
            logger.info(f"Creating PlayerGame for user: {user.username}")
            
            # Check if PlayerGame already exists for this user and game
            existing_player_game = PlayerGame.objects.filter(game=game, user=user).first()
            
            if existing_player_game:
                # Update existing PlayerGame with new board count
                existing_player_game.boards_count += int(number_of_boards)
                existing_player_game.save()
                created_player_games.append(existing_player_game)
                logger.info(f"Updated existing PlayerGame: {existing_player_game}")
            else:
                # Create new PlayerGame
                player_game = PlayerGame.objects.create(
                    game=game,
                    user=user,
                    has_bingo=False,  # Default to False, will be updated when player gets bingo
                    boards_count=int(number_of_boards)
                )
                created_player_games.append(player_game)
                logger.info(f"Created new PlayerGame: {player_game}")
                
        except Exception as e:
            logger.error(f"Error creating PlayerGame for player {player_telegram_id}: {e}")
    
    logger.info(f"Created/Updated {len(created_player_games)} PlayerGame entries")
    return created_player_games


