const { markPlayerCard } = require('./bingo');
const { checkSingleCardBingo } = require('./singleBingo');
const { endGame } = require('./endGame');
const { gameWinWallet } = require('./api');

async function handleBingo(data, activeGames, io, gameIntervals, users) {
  const { gameId, playerId, board, boardNumber, playerName, roomId } = data;

  const game = activeGames.get(gameId);
  if (!game || game.status !== 'in-progress') return;

  const playerCards = game.players.get(playerId);
  if (!playerCards || !Array.isArray(playerCards)) return;

  // Optional: Validate submitted board belongs to player
  if (!playerCards.some(card => JSON.stringify(card) === JSON.stringify(board))) {
    console.warn(`Submitted board does not belong to player ${playerId}`);
    return;
  }

  const markedCard = markPlayerCard(board, game.calledNumbers);
  const isBingo = checkSingleCardBingo(markedCard);

  if (isBingo) {
    // ✅ Prevent multiple winners
    if (game.winner) {
      console.log(`Late bingo by ${playerId}, but winner is already ${game.winner}`);
      io.to(game.roomId).emit("lateWin", {
        playerId,
        message: "Bingo already claimed by another player.",
        winner: game.winner
      });
      return;
    }

    // Set the first winner
    game.winner = playerId;

    console.log(`Player ${playerName} (${playerId}) got BINGO FIRST!`);

    io.to(game.roomId).emit("winBingo", {
      isBingo: true,
      playerId,
      markedCells: markedCard,
      winningCard: markedCard,
      winner: playerId,
      calledNumbers: game.calledNumbers,
      playerCard: boardNumber,
      winner_Number: boardNumber,
      playerName,
      currentCall: game.currentCall,
      gameId,
      total_winAmount: game.total_winAmount,
      total_players: game.total_players,
      roomId
    });

    try {
      await gameWinWallet(playerId, roomId, game.total_winAmount);
      console.log(`Wallet credited for player ${playerId}`);
    } catch (error) {
      console.error("Error processing win wallet:", error);
    }

    try {
      await endGame(game, gameIntervals, users, io, activeGames);
    } catch (err) {
      console.error("Error ending game:", err);
    }
  } else {
    console.log(`False bingo from player ${playerId} on board ${boardNumber}`);
    io.to(game.roomId).emit("falseBingo", {
      isBingo: false,
      playerId,
      losser_board: boardNumber,
    });
  }
}

module.exports = { handleBingo };
