const express = require('express');
const router = express.Router();
const { getAllGames, getGameById, createGame, updateGame, deleteGame, addPlayerToGame } = require('../controllers/games');

// GET /api/games - Get all games
router.get('/', getAllGames);

// GET /api/games/:id - Get game by ID
router.get('/:id', getGameById);

// POST /api/games - Create new game
router.post('/', createGame);

// PUT /api/games/:id - Update game by ID
router.put('/:id', updateGame);

// POST /api/games/add-player - Add player to game
router.post('/add-player', addPlayerToGame);

// DELETE /api/games/:id - Delete game by ID
router.delete('/:id', deleteGame);

module.exports = router;
