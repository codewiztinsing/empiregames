const { getConstant } = require('./constants');

async function createGame(roomId,activeGames) {
    const gameSettings = await getConstant();
  
  
    const game = {
      id: roomId,
      players: new Map(), // Map<playerId, Board[]>
      numberOfBoardsToPlayer: new Map(),
      selectedNumbersToPlayer: new Map(),
      playersLeftBeforeStart:[],
      total_players: 0,
      total_winAmount: 0, 
      calledNumbers: [],
      selectedNumbers: [],
      currentCall: null,
      status: 'waiting',
      winner: null,
      gameOver: false,
      countDown: gameSettings.countDown,
      isCountStart: false,
      gameSpeed:gameSettings.gameSpeed,
      roomId
    };
    activeGames.set(roomId, game);
    return game;
  }
  

module.exports = { createGame };
  
  