const express = require('express');
const router = express.Router();
const { getDashboardStats, getDashboardRecentStats } = require('../controllers/dashboard');

// GET /api/v1/dashboard/stats - Get dashboard statistics
router.get('/stats', getDashboardStats);

// GET /api/v1/dashboard/stats/recent - Get dashboard recent statistics
router.get('/stats/recent', getDashboardRecentStats);


module.exports = router;
