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
      valueType,
      minDeposit, 
      maxBonus, 
      startDate, 
      endDate, 
      isActive, 
      terms 
    } = req.body;

    // Set default dates if not provided
    const today = new Date();
    const oneWeekFromToday = new Date(today.getTime() + (7 * 24 * 60 * 60 * 1000));
    
    // Validate dates
    const validStartDate = startDate ? new Date(startDate) : today;
    const validEndDate = endDate ? new Date(endDate) : oneWeekFromToday;

    // Check if dates are valid
    if (startDate && isNaN(validStartDate.getTime())) {
      return res.status(400).json({ error: 'Invalid start date format' });
    }
    if (endDate && isNaN(validEndDate.getTime())) {
      return res.status(400).json({ error: 'Invalid end date format' });
    }

    const promotion = await prisma.promotion.create({
      data: {
        title,
        description,
        type,
        value: parseFloat(value),
        valueType: valueType || 'fixed', // Default to 'fixed' if not provided
        minDeposit: minDeposit ? parseFloat(minDeposit) : null,
        maxBonus: maxBonus ? parseFloat(maxBonus) : null,
        startDate: validStartDate,
        endDate: validEndDate,
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
      valueType,
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
    if (valueType) updateData.valueType = valueType;
    if (minDeposit) updateData.minDeposit = parseFloat(minDeposit);
    if (maxBonus) updateData.maxBonus = parseFloat(maxBonus);
    
    // Validate dates before adding to updateData
    if (startDate) {
      const validStartDate = new Date(startDate);
      if (isNaN(validStartDate.getTime())) {
        return res.status(400).json({ error: 'Invalid start date format' });
      }
      updateData.startDate = validStartDate;
    }
    if (endDate) {
      const validEndDate = new Date(endDate);
      if (isNaN(validEndDate.getTime())) {
        return res.status(400).json({ error: 'Invalid end date format' });
      }
      updateData.endDate = validEndDate;
    }
    
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
