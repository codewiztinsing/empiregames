const express = require('express');
const router = express.Router();
const { getPlayerBalance, handlePlayerWin, handlePlayerLoss, handleBatchPlayerLoss, updatePlayerBalance } = require('../controllers/wallet');

// GET /api/wallet/player/:id - Get player balance
router.get('/player/:id', getPlayerBalance);

// POST /api/wallet/win - Handle player win
router.post('/win', handlePlayerWin);

// POST /api/wallet/loss - Handle player loss
router.post('/loss', handlePlayerLoss);

// POST /api/wallet/batch-loss - Handle batch player loss
router.post('/batch-loss', handleBatchPlayerLoss);

// POST /api/wallet/update-balance - Update player balance (admin)
router.post('/update-balance', updatePlayerBalance);

module.exports = router;
