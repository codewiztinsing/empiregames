const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/games - Get all games
const getAllGames = async (req, res) => {
  try {
    const games = await prisma.game.findMany({
      include: {
        players: true
      }
    });
    res.json(games);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch games' });
  }
};

// GET /api/games/:id - Get game by ID
const getGameById = async (req, res) => {
  try {
    const { id } = req.params;
    const game = await prisma.game.findUnique({
      where: { id: parseInt(id) },
      include: {
        players: true
      }
    });
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    res.json(game);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch game' });
  }
};

// POST /api/games - Create new game
const createGame = async (req, res) => {
  try {
    const { betAmount } = req.body;
    
    if (!betAmount) {
      return res.status(400).json({ error: 'Bet amount is required' });
    }
    
    const game = await prisma.game.create({
      data: {
        betAmount
      }
    });
    
    res.status(201).json(game);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to create game' });
  }
};

// PUT /api/games/:id - Update game by ID
const updateGame = async (req, res) => {
  try {
    const { id } = req.params;
    const { betAmount } = req.body;
    
    const updateData = {};
    if (betAmount) updateData.betAmount = betAmount;
    
    const game = await prisma.game.update({
      where: { id: parseInt(id) },
      data: updateData,
      include: {
        players: true
      }
    });
    
    res.json(game);
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Game not found' });
    }
    console.log(error);
    res.status(500).json({ error: 'Failed to update game' });
  }
};

// DELETE /api/games/:id - Delete game by ID
const deleteGame = async (req, res) => {
  try {
    const { id } = req.params;
    
    await prisma.game.delete({
      where: { id: parseInt(id) }
    });
    
    res.json({ message: 'Game deleted successfully' });
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Game not found' });
    }
    console.log(error);
    res.status(500).json({ error: 'Failed to delete game' });
  }
};


const addPlayerToGame = async (req, res) => {
  try {
    const { gameId, playerId } = req.body;
    const game = await prisma.game.findUnique({
      where: { id: parseInt(gameId) }
    });
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    const player = await prisma.player.findUnique({
      where: { id: parseInt(playerId) }
    });
    if (!player) {  
      return res.status(404).json({ error: 'Player not found' });
    }
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to add player to game' });
  }
}

module.exports = {
  getAllGames,
  getGameById,
  createGame,
  updateGame,
  deleteGame,
  addPlayerToGame
};
