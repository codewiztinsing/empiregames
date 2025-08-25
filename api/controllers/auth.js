const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

// POST /api/v1/auth/login - User login
const login = async (req, res) => {
  try {
    const { username    , password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    // Find user by username
    const user = await prisma.admin.findFirst({
      where: { username }
    });

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT tokens
    const accessToken = jwt.sign(
      { userId: user.id, telegramId: user.telegramId, username: user.username },
      process.env.JWT_SECRET,
      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_REFRESH_SECRET,
      { expiresIn: '7d' }
    );



    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        telegramId: user.telegramId,
        username: user.username,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/v1/auth/register - User registration
const register = async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    // Check if user already exists
    const existingUser = await prisma.player.findFirst({
      where: {
        OR: [
          { username }
        ]
      }
    });

    if (existingUser) {
      return res.status(409).json({ error: 'User with this username already exists' });
    }

    // Hash password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Create user
    const user = await prisma.admin.create({
      data: {
        username,
        password: hashedPassword,
        role: 'admin',
        status: 'active'
      }
    });
    console.log("process.env.JWT_SECRET ",process.env.JWT_SECRET);

    // Generate JWT tokens
    const accessToken = jwt.sign(
      { userId: user.id, telegramId: user.telegramId, username: user.username },
      process.env.JWT_SECRET,

      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_REFRESH_SECRET,
      { expiresIn: '7d' }
    );


    res.status(201).json({
      message: 'Registration successful',
      user: {
        id: user.id,
        username: user.username,
      },
      accessToken,
      refreshToken
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/v1/auth/logout - User logout
const logout = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token is required' });
    }

    // Find user by refresh token and clear it
    const user = await prisma.admin.findFirst({
      where: { refreshToken }
    });

    if (user) {
      await prisma.admin.update({
        where: { id: user.id },
        data: { refreshToken: null }
      });
    }

    res.json({ message: 'Logout successful' });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

// POST /api/v1/auth/refresh - Refresh access token
const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({ error: 'Refresh token is required' });
    }

    // Verify refresh token
    let decoded;
    try {
      decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    } catch (error) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }

    // Find user with this refresh token\
    const user = await prisma.admin.findFirst({
      where: {
        id: decoded.userId,
        refreshToken
      }
    });

    if (!user) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }

    // Generate new access token
    const accessToken = jwt.sign(
      { userId: user.id, telegramId: user.telegramId, username: user.username },
      process.env.JWT_SECRET,
      { expiresIn: '15m' }
    );

    res.json({
      accessToken,
      user: {
        id: user.id,
        telegramId: user.telegramId,
        username: user.username,
        role: user.role,
        status: user.status
      }
    });
  } catch (error) {
    console.error('Refresh token error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = {
  login,
  register,
  logout,
  refreshToken
};
