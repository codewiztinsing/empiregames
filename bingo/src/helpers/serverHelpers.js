// serverHelpers.js
// Helper utilities for server.js logic (non-breaking extractions)

/**
 * Compute and update totals on the game object based on selectedNumbers.
 * Includes fake picks because they are stored in selectedNumbers.
 */
function computeTotals(game) {
  const selected = (game.selectedNumbers || []).filter(n => n !== null);
  const totalPlayers = selected.length;
  const realPlayers = game.players ? game.players.size : 0;
  const fakePlayers = Math.max(0, totalPlayers - realPlayers);
  const winAmount = totalPlayers * game.roomId * 0.78;
  game.total_players = totalPlayers;
  game.total_winAmount = winAmount;
  game.win_amount = winAmount;
  return { selected, totalPlayers, realPlayers, fakePlayers, winAmount };
}

/**
 * Emit gameState with consistent fields; accepts optional overrides.
 */
function emitGameState(io, game, overrides = {}) {
  const payload = {
    gameId: game.id,
    roomId: game.roomId,
    pickedNumbers: game.selectedNumbers,
    game_status: game.status,
    count_down: game.countDown,
    win_amount: game.total_winAmount || game.win_amount || 0,
    total_players: game.total_players || 0,
    lastBall: game.currentCall,
    called_numbers: game.calledNumbers,
    total_called_numbers: game.calledNumbers ? game.calledNumbers.length : 0,
    ...overrides,
  };
  io.emit("gameState", payload);
}

module.exports = {
  computeTotals,
  emitGameState,
};


