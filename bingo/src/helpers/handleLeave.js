const { getWaitingGames } = require('./getWaitingGames');
async function handleLeave(data,activeGames,io){
    const game = activeGames.get(data.roomId);
    const playerId = data.playerId;
    

    if (game?.players.has(playerId)) {
      game.players.delete(playerId);
    }
  
    
    const selectedCard = data.selectedNumber
    const selectedCard2 = data.selectedNumber2

    console.log("selectedCard",selectedCard)
    console.log("selectedCard2",selectedCard2)
    if (!game) return;
    if (selectedCard && game.selectedNumbers.includes(selectedCard)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard);
    }
    if (selectedCard2 && selectedCard2 !== null && game.selectedNumbers.includes(selectedCard2)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard2 && num !== null);
    }
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  
    io.emit("waitingGames",   [...getWaitingGames(activeGames),...getWaitingGames(activeGames,"waiting")]);
    
}

module.exports = { handleLeave };