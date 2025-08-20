
function handleRefresh(data,activeGames,io){
    console.log("handleRefresh", data)
    const game = activeGames.get(data.gameId);
    if (!game) return;
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      total_players: game.total_players,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.total_winAmount,
      lastBall: game.currentCall,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length
    });
  
  }

module.exports = { handleRefresh };