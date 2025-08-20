function getWaitingGames(activeGames,status="in-progress") {
    const waitingGames = [];
    for (const game of activeGames.values()) {
      if (game.status === status) {
        const isDuplicate = waitingGames.some(existingGame => existingGame.id === game.id);
        if (isDuplicate) continue;
        waitingGames.push({
          id: game.id,
          betAmount: game.roomId,
          players: game.players.size,
          status: game.status
        });
      }
    }
    return waitingGames;
  }
  
module.exports = { getWaitingGames };