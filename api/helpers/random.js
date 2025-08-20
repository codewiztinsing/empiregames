const generateRandomName = () => {
  const adjectives = ['Abebe', 'Alemu', 'Bekele', 'Desta', 'Fikru', 'Girma', 'Haile', 'Kebede', 'Mulatu', 'Tadesse'];
  const nouns = ['Assefa', 'Bogale', 'Demeke', 'Gebre', 'Mekonen', 'Negash', 'Teshome', 'Welde', 'Yilma', 'Zewde'];
  
  const randomAdjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
  return `${randomAdjective}${randomNoun}${Math.floor(Math.random() * 1000)}`;
};

const createRandomPlayer = () => {
  return {
    playerId: Math.random().toString(36).substr(2, 9),
    playerName: generateRandomName(),
    betAmount:10 // Random bet between 100-1000
  };
};

const simulateRandomPlayers = (socket, gameId) => {
  const minInterval = 2000; // Minimum 2 seconds
  const maxInterval = 8000; // Maximum 8 seconds
  
  const joinGame = () => {
    const player = createRandomPlayer();
    
    socket.emit('joinGame', {
      gameId: gameId,
      playerId: player.playerId,
      playerName: player.playerName,
      betAmount: player.betAmount
    });

    // Schedule next random player
    const nextInterval = Math.floor(Math.random() * (maxInterval - minInterval)) + minInterval;
    setTimeout(joinGame, nextInterval);
  };

  // Start the simulation
  joinGame();
};

export { simulateRandomPlayers };
