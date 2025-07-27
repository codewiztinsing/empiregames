const { clearGameIntervals } = require('./handleClearGameIntervals');
const { getWaitingGames } = require('./getWaitingGames');

const { endGame } = require('./src/helpers/endGame');

async function startGame(game,io,activeGames,gameIntervals) {
    game.status = "in-progress";
    io.emit("waitingGames",   getWaitingGames(activeGames,"in-progress"));
    clearGameIntervals(gameIntervals,game.id);
  
    io.emit("gameStatus",{
      roomId: game.roomId,
      game_status: "in-progress"
    })
  
    const players = Array.from(game.players.keys()).map(playerId => ({
      playerId: playerId,
      numberOfBoards: game.numberOfBoardsToPlayer.get(playerId)
    }));
  
   
    try {
      await gameLossWallet(players, game.roomId);
    } catch (error) {
      console.error('Error charging players:', error);
    }
  
    const gameInterval = setInterval(() => {
      const calledSet = new Set(game.calledNumbers.map(b => b.number));
      let ball = generateBalls();
      while (calledSet.has(ball.number)) {
        ball = generateBalls();
      }
      game.currentCall = ball;
      game.calledNumbers.push(ball);
      game.selectedNumbers = [];
      io.emit("pickedNumbers",game.selectedNumbers)
    
      io.to(game.roomId).emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: game.selectedNumbers,
        game_status: game.status,
        count_down: game.countDown,
        win_amount: game.roomId * game.players.size * 0.8,
        lastBall: ball,
        called_numbers: game.calledNumbers,
        total_called_numbers: game.calledNumbers.length
      });
     
  
      if (game.calledNumbers.length >= 75) {
        io.emit("gameStatus", {
          roomId: game.roomId,
          game_status: "waiting"
        })
        endGame(game);
      }
    }, game.gameSpeed);
   
  
    gameIntervals.set(game.id, [gameInterval]);
  }

  module.exports = { startGame };
  