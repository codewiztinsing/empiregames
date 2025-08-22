
function handleDisconnect(io,socket,activeGames,users,gameIntervals){
    const user = users.get(socket.id);
    if(!user) return;
    const game = activeGames.get(user.gameId);

    console.log(`User disconnected: ${socket.id}`, {
      userId: user?.playerId,
      gameId: user?.gameId,
      timestamp: new Date().toISOString(),
      
    });
  
    if (user) {

      if (game?.players.has(user.playerId)) {
        console.log("game.status",game.status)
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          game.playersLeftBeforeStart.push(user.playerId)
          io.emit("gameState", {
            message: `User ${user.playerId} disconnected`,
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers.filter(num => !game.selectedNumbersToPlayer.get(user.playerId)?.includes(num)),
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