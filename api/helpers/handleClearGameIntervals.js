

function clearGameIntervals(gameIntervals,gameId) {
    if (gameIntervals.has(gameId)) {
      gameIntervals.get(gameId).forEach(clearInterval);
      gameIntervals.delete(gameId);
    }
  }

module.exports = { clearGameIntervals };