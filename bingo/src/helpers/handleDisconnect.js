
function handleDisconnect(io,socket,activeGames,users,gameIntervals){
    const user = users.get(socket.id);
  
    if (user) {
      const game = activeGames.get(user.gameId);
      if (game?.players.has(user.playerId)) {
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          game.playersLeftBeforeStart.push(user.playerId)
          io.to(game.roomId).emit("gameState", {
            message: `User ${user.playerId} disconnected`,
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers,
            total_players: game.total_players,
            game_status: game.status,
            count_down: game.countDown
          });
          users.delete(socket.id);
        }
       
    }
    }
  }


module.exports = { handleDisconnect };