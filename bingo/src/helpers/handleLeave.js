const { getWaitingGames } = require('./getWaitingGames');

async function handleLeave(data, activeGames, io) {
  const game = activeGames.get(data.roomId);
  const playerId = data.playerId;
  const selectedCard = data.selectedNumber;
  const selectedCard2 = data.selectedNumber2;

  // If no game or no playerId provided, exit early
  if (!game || !playerId) return;

  // Remove the player from the game
  if (game.players.has(playerId)) {
    game.players.delete(playerId);
  }

  // Remove the player's selected numbers from the global pool
  if (selectedCard != null) {
    game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard);
  }

  if (selectedCard2 != null) {
    game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard2);
  }

  // Remove mappings related to the player
  game.selectedNumbersToPlayer.delete(playerId);
  game.numberOfBoardsToPlayer.delete(playerId);

  // Recalculate total_players based on remaining selected numbers
  game.total_players = 0;
  for (const player of game.players.keys()) {
    const numbers = game.selectedNumbersToPlayer.get(player) || [];
    game.total_players += numbers.length;
  }

  // Recalculate win amount based on updated total players
  const betAmount = Number(game.betAmount || game.roomId); // Fallback if no betAmount
  game.total_winAmount = game.total_players * betAmount * 0.8;

  // Emit updated picked numbers to the room
  io.to(game.roomId).emit("pickedNumbers", {
    roomId: game.roomId,
    numbers: game.selectedNumbers
  });

  // Emit updated waiting game list to all users
  io.emit("waitingGames", [
    ...getWaitingGames(activeGames),
    ...getWaitingGames(activeGames, "waiting")
  ]);

  // Optional: Clean up game if empty
  if (game.players.size === 0) {
    activeGames.delete(game.roomId);
    console.log(`Game ${game.roomId} has been deleted due to no active players.`);
  }
}

module.exports = { handleLeave };
