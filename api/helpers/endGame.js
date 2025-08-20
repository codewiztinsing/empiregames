const { clearGameIntervals } = require('./handleClearGameIntervals');
const { startCountDown } = require('./handleStartCountDown');
const { getWaitingGames } = require('./getWaitingGames');
const { updateLastGame } = require('./api');

/**
 * Ends the current game, resets the game state, notifies all clients,
 * and optionally starts a new countdown if enough players remain.
 */
async function endGame(game, gameIntervals, users, io, activeGames) {
  if (!game) return;

  console.log("🔚 Ending Game:", game.id);

  // Clear active timers related to the game
  clearGameIntervals(gameIntervals, game.id);

  // Reset game state
  game.players.clear();
  game.selectedNumbers = [];
  game.selectedNumbersToPlayer?.clear?.();
  game.numberOfBoardsToPlayer?.clear?.();
  game.total_winAmount = 0;
  game.total_players = 0;
  game.calledNumbers = [];
  game.currentCall = null;
  game.status = "waiting";
  game.gameOver = false;
  game.winner = null;
  game.countDown = 30;
  game.isCountStart = false;

  // Clean up any socket-to-user references for this game
  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) {
      users.delete(socketId);
    }
  }

  // Optionally update persistent game history or DB
  await updateLastGame(game.roomId);

  // Emit updated waiting game list to all clients
  io.emit("waitingGames", [
    ...getWaitingGames(activeGames),
    ...getWaitingGames(activeGames, "waiting")
  ]);

  // Inform the game room that the game has ended
  io.to(game.roomId).emit("gameEnded", {
    roomId: game.roomId,
    status: "waiting",
    message: "Game ended. Waiting for next round.",
  });

  // Automatically restart if enough players are still in the room
  if (game.players.size >= 2) {
    console.log("⏳ Starting new countdown for next round...");
    startCountDown(game, io, activeGames, gameIntervals, users);
  }

  console.log(`✅ Game ${game.roomId} has been reset and is waiting for players.`);
}

module.exports = { endGame };
