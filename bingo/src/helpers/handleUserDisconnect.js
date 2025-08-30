module.exports = function handleUserDisconnect(socket){
    const user = users.get(socket.id);
    console.log("user",user)
    if (user) {
      const game = activeGames.get(user.gameId);
      const playerId = user.playerId
   
      if(game.selectedNumbersToPlayer.has(playerId)){
        const selectedNumber = game.selectedNumbersToPlayer.get(playerId)[0]
        const selectedNumber2 = game.selectedNumbersToPlayer.get(playerId)[1]
        game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber);
        game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber2);
      }
     
 
      if (game?.players.has(user.playerId)) {
        console.log("game.status",game.status)
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          if(game.selectedNumbersToPlayer.has(playerId)){
            const selectedNumber = game.selectedNumbersToPlayer.get(playerId)[0]
            const selectedNumber2 = game.selectedNumbersToPlayer.get(playerId)[1]
          }
          game.selectedNumbers = game?.selectedNumbers?.filter(num => num !== selectedNumber);
          game.selectedNumbers = game?.selectedNumbers?.filter(num => num !== selectedNumber2);
    
    
          io.to(game.roomId).emit("gameState", {
            message: `User ${user.playerId} disconnected`,
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers.filter(num => num !== selectedNumber && num !== selectedNumber2),
            total_players: game.selectedNumbers.length,
            game_status: game.status,
            count_down: game.countDown
          });


        
          game.selectedNumbersToPlayer.delete(playerId)
          game.selectedNumbersToPlayer.delete(playerId)
          io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
          users.delete(socket.id);
          users.delete(socket.id);
          users.delete(socket.id);

        }
       
    }
    }
}
   
