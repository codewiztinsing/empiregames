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
      user = await prisma.player.findFirst({
        where: { telegramId: `${telegramId}` }
      });
    } catch (uniqueError) {
      // If findUnique fails (e.g., telegramId not unique yet), fall back to findFirst
      console.log("Fallback to findFirst due to:", uniqueError.message);
      user = await prisma.player.findFirst({
        where: { telegramId: telegramId }
      });
    }
    

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
};


// GET /api/users/balance/:telegramId - Get user balance
const getUserBalance = async (req, res) => {
  try {
    const { telegramId } = req.params;
    console.log("telegramId = ",telegramId)
    console.log("telegramId type = ",typeof telegramId)
    console.log("telegramId = ",telegramId)
    const user = await prisma.player.findFirst({
      where: { telegramId: `${telegramId}` }
    });
    if (!user) {
      console.log("User not found")
      return res.status(404).json({ error: 'User not found' });
    }
    res.json({
      balance: user.balance,
      username: user.username,
      telegramId: user.telegramId,
      phoneNumber: user.phoneNumber
    });
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch user balance' });
  }
};

// POST /api/users - Create new user
const createUser = async (req, res) => {
  console.log("createUser");

  try {
    const { username, telegramId, phoneNumber } = req.body;

    
    if (!username || !telegramId || !phoneNumber) {
      console.log("Username, telegramId and phoneNumber are required");
      return res.status(400).json({ error: 'Username, telegramId and phoneNumber are required' });
    }
    
    // Check if user already exists
    const existingUser = await prisma.player.findFirst({
      where: { telegramId: `${telegramId}` }
    });
    
    if (existingUser) {
      console.log("User with this telegramId already exists");
      return res.status(409).json({ error: 'User with this telegramId already exists' });
    }
    
    const player = await prisma.player.create({
      data: {
        username,
        telegramId: `${telegramId}`,
        phoneNumber,
        balance: 0
      }
    });
    console.log("player = ",player)
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
    const { telegramId } = req.params;
    const { username, phoneNumber, balance, status } = req.body;
    
    const updateData = {};
    if (username) updateData.username = username;
    if (phoneNumber) updateData.phoneNumber = phoneNumber;
    if (balance) updateData.balance = parseInt(balance);
    if (status) updateData.status = status;
    
    // First find the user by telegramId since it's not unique
    const existingUser = await prisma.player.findFirst({
      where: { telegramId: telegramId }
    });
    
    if (!existingUser) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Update using the unique id field
    const user = await prisma.player.update({
      where: { id: existingUser.id },
      data: updateData
    });
    
    res.json(user);
  } catch (error) {
    console.log(error);
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: 'Failed to update user' });
  }
};

// DELETE /api/users/:telegramId - Delete user by ID
const deleteUser = async (req, res) => {
  try {
    const { telegramId } = req.params;
    console.log("telegramId = ",telegramId)
    
    // First find the user by telegramId since it's not unique
    const existingUser = await prisma.player.findFirst({
      where: { telegramId: telegramId }
    });
    
    if (!existingUser) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Delete using the unique id field
    await prisma.player.delete({
      where: { id: existingUser.id }
    });
    
    res.status(204).send();
  } catch (error) {
    console.log("error = ",error)
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: 'Failed to delete user' });
  }
};

module.exports = {
  getAllUsers,
  getUserById,
  getUserBalance,
  createUser,
  updateUser,
  deleteUser
};
