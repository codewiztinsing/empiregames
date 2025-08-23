const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/users - Get all users
const getAllUsers = async (req, res) => {
  try {
    const users = await prisma.player.findMany();
    res.json(users);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
};

// GET /api/users/:id - Get user by ID
const getUserById = async (req, res) => {
  try {
    const { telegramId } = req.params;
    console.log("telegramId = ",telegramId)
    
    // Try to find user by telegramId
    let user;
    try {
      user = await prisma.player.findUnique({
        where: { telegramId: telegramId }
      });
    } catch (uniqueError) {
      // If findUnique fails (e.g., telegramId not unique yet), fall back to findFirst
      console.log("Fallback to findFirst due to:", uniqueError.message);
      user = await prisma.player.findFirst({
        where: { telegramId: telegramId }
      });
    }
    
    console.log("user = ",user)

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
};

// POST /api/users - Create new user
const createUser = async (req, res) => {
    console.log("createUser");
    console.log(req.body);
  try {
    const { username, telegramId, phoneNumber } = req.body;
    console.log(req.body);
    
    if (!username || !telegramId || !phoneNumber) {
      return res.status(400).json({ error: 'Username, telegramId and phoneNumber are required' });
    }
    
    // Check if user already exists
    const existingUser = await prisma.player.findFirst({
      where: { telegramId: telegramId }
    });
    
    if (existingUser) {
      return res.status(409).json({ error: 'User with this telegramId already exists' });
    }
    
    const player = await prisma.player.create({
      data: {
        username,
        telegramId,
        phoneNumber,
        balance: 0
      }
    });
    
    res.status(201).json(player);
  } catch (error) {
    console.log(error);
    if (error.code === 'P2002') {
      return res.status(409).json({ error: 'User with this telegramId already exists' });
    }
    res.status(500).json({ error: 'Failed to create user' });
  }
};

// PUT /api/users/:id - Update user by ID
const updateUser = async (req, res) => {
  try {
    const { id } = req.params;
    const { name, gameId } = req.body;
    
    const updateData = {};
    if (name) updateData.name = name;
    if (gameId) updateData.gameId = parseInt(gameId);
    
    const user = await prisma.player.update({
      where: { id: parseInt(id) },
      data: updateData,
      include: {
        game: true
      }
    });
    
    res.json(user);
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: 'Failed to update user' });
  }
};

// DELETE /api/users/:id - Delete user by ID
const deleteUser = async (req, res) => {
  try {
    const { id } = req.params;
    
    await prisma.player.delete({
      where: { id: parseInt(id) }
    });
    
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: 'Failed to delete user' });
  }
};

module.exports = {
  getAllUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser
};
