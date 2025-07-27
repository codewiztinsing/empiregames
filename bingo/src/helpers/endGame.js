
async  function endGame(game,gameIntervals,users) {
  clearGameIntervals(gameIntervals,game.id);
  game.players.clear();
  game.calledNumbers = [];
  game.currentCall = null;
  game.status = "waiting";
  game.gameOver = false;
  game.winner = null;
  game.countDown = 30;
  game.isCountStart = false;

  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) users.delete(socketId);
  }

  const data = await updateLastGame(game.roomId);
  startCountDown(game);
}

module.exports = { endGame };
