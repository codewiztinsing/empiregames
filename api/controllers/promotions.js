const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/promotions - Get all promotions
const getPromotions = async (req, res) => {
  try {
    const promotions = await prisma.promotion.findMany({
      orderBy: { createdAt: 'desc' }
    });
    
    res.json(promotions);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch promotions' });
  }
};

// GET /api/promotions/:id - Get promotion by ID
const getPromotionById = async (req, res) => {
  try {
    const { id } = req.params;
    
    const promotion = await prisma.promotion.findUnique({
      where: { id: parseInt(id) }
    });

    if (!promotion) {
      return res.status(404).json({ error: 'Promotion not found' });
    }

    res.json(promotion);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to fetch promotion' });
  }
};

// POST /api/promotions - Create new promotion
const createPromotion = async (req, res) => {
  try {
    const { 
      title, 
      description, 
      type, 
      value, 
      minDeposit, 
      maxBonus, 
      startDate, 
      endDate, 
      isActive, 
      terms 
    } = req.body;

    const promotion = await prisma.promotion.create({
      data: {
        title,
        description,
        type,
        value: parseFloat(value),
        minDeposit: minDeposit ? parseFloat(minDeposit) : null,
        maxBonus: maxBonus ? parseFloat(maxBonus) : null,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        isActive: isActive || false,
        terms
      }
    });

    res.status(201).json(promotion);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Failed to create promotion' });
  }
};

// PUT /api/promotions/:id - Update promotion
const updatePromotion = async (req, res) => {
  try {
    const { id } = req.params;
    const { 
      title, 
      description, 
      type, 
      value, 
      minDeposit, 
      maxBonus, 
      startDate, 
      endDate, 
      isActive, 
      terms 
    } = req.body;

    const updateData = {};
    if (title) updateData.title = title;
    if (description) updateData.description = description;
    if (type) updateData.type = type;
    if (value) updateData.value = parseFloat(value);
    if (minDeposit) updateData.minDeposit = parseFloat(minDeposit);
    if (maxBonus) updateData.maxBonus = parseFloat(maxBonus);
    if (startDate) updateData.startDate = new Date(startDate);
    if (endDate) updateData.endDate = new Date(endDate);
    if (isActive !== undefined) updateData.isActive = isActive;
    if (terms) updateData.terms = terms;

    const promotion = await prisma.promotion.update({
      where: { id: parseInt(id) },
      data: updateData
    });

    res.json(promotion);
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Promotion not found' });
    }
    console.log(error);
    res.status(500).json({ error: 'Failed to update promotion' });
  }
};

// DELETE /api/promotions/:id - Delete promotion
const deletePromotion = async (req, res) => {
  try {
    const { id } = req.params;
    
    await prisma.promotion.delete({
      where: { id: parseInt(id) }
    });
    
    res.json({ message: 'Promotion deleted successfully' });
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Promotion not found' });
    }
    console.log(error);
    res.status(500).json({ error: 'Failed to delete promotion' });
  }
};

module.exports = {
  getPromotions,
  getPromotionById,
  createPromotion,
  updatePromotion,
  deletePromotion
};
