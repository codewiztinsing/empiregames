const { startCountDown } = require('./handleStartCountDown');
const { clearGameIntervals } = require('./handleClearGameIntervals');

function handleJoin(io, socket, data, activeGames, users, gameIntervals) {
  const game = activeGames.get(data.roomId);
  console.log("game data", game)
    console.log("game", game)
  if (!data.playerId || !game) return;

  // Reject if game is already in progress
  if (game.status === 'active') {
    socket.emit('joinError', {
      roomId: data.roomId,
      playerId: data.playerId,
      message: 'Game is already in progress. Please wait for the next round.'
    });
    return;
  }

  // Reject if already joined
  if (game.players.has(data.playerId)) {
    socket.emit('joinError', {
      roomId: data.roomId,
      playerId: data.playerId,
      message: 'Already in game. Finish or leave current game.'
    });
    return;
  }

  // Reject if room is full
  if (game.players.size >= 100) {
    socket.emit('joinError', {
      roomId: data.roomId,
      playerId: data.playerId,
      message: 'Room is full (max 100 players).'
    });
    return;
  }

  // Add selected numbers
  if (data.selectedNumber != null) {
    game.selectedNumbers.push(data.selectedNumber);
  }
  if (data.selectedNumber2 != null) {
    game.selectedNumbers.push(data.selectedNumber2);
  }

  const playerNumbers = [data.selectedNumber];
  if (data.selectedNumber2 != null) {
    playerNumbers.push(data.selectedNumber2);
  }
  game.selectedNumbersToPlayer.set(data.playerId, playerNumbers);

  // Store number of boards
  game.numberOfBoardsToPlayer.set(data.playerId, data.numberOfBoards);

  // Notify room about picked numbers
  io.to(data.roomId).emit("pickedNumbers", {
    roomId: game.roomId,
    numbers: game.selectedNumbers
  });



  // Add boards
  const boards = [data.selectBoard];
  if (data.selectBoard2) {
    boards.push(data.selectBoard2);
  }
  game.players.set(data.playerId, boards);

  // Recalculate total players and win amount
  game.total_players = 0;
  for (const player of game.players.keys()) {
    const numbers = game.selectedNumbersToPlayer.get(player) || [];
    game.total_players += numbers.length;
  }

  const betAmount = Number(game.betAmount || game.roomId); // fallback if no game.betAmount
  game.total_winAmount = game.total_players * betAmount * 0.8;
  const data_for_client = {
    gameId: game.id,
    roomId: game.roomId,
    pickedNumbers: game.selectedNumbers,
    total_players: game.total_players,
    game_status: game.status,
    count_down: game.countDown,
    players: game.players
  }

 
  // Emit updated game state
  io.to(game.roomId).emit("gameState", data_for_client);
  


  // Start countdown if enough players and countdown not started
  if (!game.isCountStart && game.players.size >= 2) {
    startCountDown(game, io, activeGames, gameIntervals, users);
  }

  console.log("game selected numbers  ",game.selectedNumbers)
  // Track socket info
  users.set(socket.id, {
    playerId: data.playerId,
    roomId: data.roomId,
    gameId: game.id
  });
}

module.exports = { handleJoin };
