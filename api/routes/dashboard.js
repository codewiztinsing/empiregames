const express = require('express');
const router = express.Router();
const { getDashboardStats } = require('../controllers/dashboard');

// GET /api/v1/dashboard/stats - Get dashboard statistics
router.get('/stats', getDashboardStats);


module.exports = router;
