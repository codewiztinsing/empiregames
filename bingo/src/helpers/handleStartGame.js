const { clearGameIntervals } = require('./handleClearGameIntervals');
const { getWaitingGames } = require('./getWaitingGames');
const { gameLossWallet } = require('./api');
const { endGame } = require('./endGame');
const { generateBalls } = require('./ball');

async function startGame(game,io,activeGames,gameIntervals,users) {
    game.status = "active";
    io.emit("waitingGames",   getWaitingGames(activeGames,"active"));
    clearGameIntervals(gameIntervals,game.id);
  
    io.emit("gameStatus",{
      roomId: game.roomId,
      game_status: "active"
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
      game.total_winAmount = (game.selectedNumbers?.filter(num => num !== null)?.length || 0) * game.roomId * 0.8;
      game.selectedNumbers = [];
      io.emit("pickedNumbers",game.selectedNumbers)
      const data_for_client = {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: game.selectedNumbers,
        game_status: game.status,
        count_down: game.countDown,

        win_amount: game.roomId * game.players.size * 0.8,
        total_players: game.players.size,
        currentCall: ball,
        total_called_numbers: game.calledNumbers.length,
        lastBall: ball,
        called_numbers: game.calledNumbers,
        total_called_numbers: game.calledNumbers.length
      }
      console.log("data_for_client", data_for_client)
      io.to(game.roomId).emit("gameState", data_for_client);
     
  
      if (game.calledNumbers.length >= 75) {
        io.emit("gameStatus", {
          roomId: game.roomId,
          game_status: "waiting"
        })
        endGame(game,gameIntervals,users,io,activeGames);
      }
    }, game.gameSpeed);
   
  
    gameIntervals.set(game.id, [gameInterval]);
  }

  module.exports = { startGame };
  