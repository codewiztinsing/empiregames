const { clearGameIntervals } = require('./handleClearGameIntervals');
const { startCountDown } = require('./handleStartCountDown');
const { getWaitingGames } = require('./getWaitingGames');
const { updateLastGame } = require('./api');

async  function endGame(game,gameIntervals,users,io,activeGames) {
  console.log("endGame",game.id)  
  console.log("gameIntervals",gameIntervals)
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
  // startCountDown(game,io,activeGames,gameIntervals) 
}

module.exports = { endGame };
