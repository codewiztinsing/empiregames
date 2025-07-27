const { startCountDown } = require('./handleStartCountDown');
const { clearGameIntervals } = require('./handleClearGameIntervals');

function handleJoin(io,socket,data,activeGames,users,gameIntervals){
    const game = activeGames.get(data.roomId);
    if (!data.playerId || !game) return;

    if (game.status === 'in-progress') {
      socket.emit('joinError', {
        roomId: data.roomId,
        message: 'Game is already in progress. Please wait for the next round.'
      });
      return;
    }

    if (game.players.has(data.playerId)) {
      socket.emit('joinError', {
        roomId: data.roomId,
        message: 'Already in game. Finish or leave current game.'
      });
      return;
    }

    game.selectedNumbers.push(data.selectedNumber)
    if (data.selectedNumber2 !== null) {
      game.selectedNumbers.push(data.selectedNumber2)
      game.selectedNumbersToPlayer.set(data.playerId,[data.selectedNumber,data.selectedNumber2])
    } else {
      game.selectedNumbersToPlayer.set(data.playerId,[data.selectedNumber])
    }
    game.numberOfBoardsToPlayer.set(data.playerId,data.numberOfBoards)
  
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
    if (game.players.size >= 100) {
      socket.emit('joinError', {
        message: 'Room is full (max 100 players).'
      });
      return;
    }

 
  
    socket.join(data.roomId);

    const boards = [data.selectBoard];
    if (data.selectBoard2) {
      boards.push(data.selectBoard2);
    }
    game.players.set(data.playerId, boards);

    for(const player of game.players.keys()){
      game.total_players += game.selectedNumbersToPlayer.get(player).length
  }
  game.total_winAmount = game.total_players * game.roomId * 0.8

  
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.total_players,
      game_status: game.status,
      count_down: game.countDown,
      players: game.players

    });

    if (!game.isCountStart && game.players.size >= 2) {
      startCountDown(game,io,activeGames,gameIntervals);
    }

    users.set(socket.id, {
      playerId: data.playerId,
      roomId: data.roomId,
      gameId: data.roomId
    });
}


module.exports = { handleJoin };