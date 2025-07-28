const { clearGameIntervals } = require('./handleClearGameIntervals');
const { startGame } = require('./handleStartGame');

function startCountDown(game,io,activeGames,gameIntervals,users) {
 
    if (game.isCountStart || game.players.size < 2) return;
    clearGameIntervals(gameIntervals,game.id);
    game.countDown = game.countDown;
    game.isCountStart = true;
  
    const countdownInterval = setInterval(() => {
      io.to(game.roomId).emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: game.selectedNumbers.filter(num => num !== null),
        total_players: game.selectedNumbers.filter(num => num !== null).length,
        game_status: game.status,
        count_down: game.countDown
      });
  
    
  
      if (game.countDown === 0) {
        clearInterval(countdownInterval);
        game.isCountStart = false;
        game.status = "waiting";
        game.countDown = game.countDown;
        game.currentCall = null;
        game.calledNumbers = [];
        startGame(game,io,activeGames,gameIntervals,users);
      }
      game.countDown--;
    }, 1000);
  
    gameIntervals.set(game.id, [countdownInterval]);
  }

module.exports = { startCountDown };