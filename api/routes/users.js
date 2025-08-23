const express = require('express');
const router = express.Router();
const { getAllUsers, getUserById, createUser, updateUser, deleteUser } = require('../controllers/users');

// GET /api/users - Get all users
router.get('/', getAllUsers);

// GET /api/users/:id - Get user by ID
router.get('/:telegramId', getUserById);

// POST /api/users - Create new user
router.post('/', createUser);

// PUT /api/users/:id - Update user by ID
router.put('/:telegramId', updateUser);

// DELETE /api/users/:id - Delete user by ID
router.delete('/:id', deleteUser);

module.exports = router;
