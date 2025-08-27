const express = require('express');
const router = express.Router();
const { getPromotions, createPromotion, updatePromotion, deletePromotion, getPromotionById } = require('../controllers/promotions');

// GET /api/v1/promotions - Get all promotions
router.get('/', getPromotions);

// GET /api/v1/promotions/:id - Get promotion by ID
router.get('/:id', getPromotionById);

// POST /api/v1/promotions - Create new promotion
router.post('/', createPromotion);

// PUT /api/v1/promotions/:id - Update promotion
router.put('/:id', updatePromotion);

// DELETE /api/v1/promotions/:id - Delete promotion
router.delete('/:id', deletePromotion);

module.exports = router;
