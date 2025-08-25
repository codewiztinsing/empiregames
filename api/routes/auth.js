const express = require('express');
const router = express.Router();
const { login, register, logout, refreshToken } = require('../controllers/auth');

// POST /api/v1/auth/login - User login
router.post('/login', login);

// POST /api/v1/auth/register - User registration
router.post('/register', register);


// POST /api/v1/auth/logout - User logout
router.post('/logout', logout);




// POST /api/v1/auth/refresh - Refresh access token
router.post('/refresh', refreshToken);

module.exports = router;
