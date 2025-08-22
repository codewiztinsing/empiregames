const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/wallet/player/:id - Get player balance
const getPlayerBalance = async (req, res) => {
    console.log("getPlayerBalance")
  try {
    const { id } = req.params;
    const player = await prisma.player.findUnique({
      where: { id: parseInt(id) },
      select: { id: true, username: true, balance: true }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    res.json({ balance: player.balance, player });
  } catch (error) {
    console.error('Error fetching balance:', error);
    res.status(500).json({ error: 'Failed to fetch balance' });
  }
};

// POST /api/wallet/win - Handle player win
const handlePlayerWin = async (req, res) => {
    console.log("handlePlayerWin")
  try {
    const { playerId, winAmount, gameId } = req.body;
    
    if (!playerId || !winAmount || !gameId) {
      return res.status(400).json({ error: 'Player ID, win amount, and game ID are required' });
    }
    
    if (winAmount <= 0) {
      return res.status(400).json({ error: 'Win amount must be positive' });
    }
    
    const player = await prisma.player.update({
      where: { id: parseInt(playerId) },
      data: {
        balance: {
          increment: parseFloat(winAmount)
        }
      }
    });
    
    // Log the transaction
    console.log(`Player ${playerId} won ${winAmount} in game ${gameId}. New balance: ${player.balance}`);
    
    res.json({ 
      success: true, 
      newBalance: player.balance, 
      winAmount: parseFloat(winAmount),
      message: 'Win amount added to balance successfully' 
    });
  } catch (error) {
    console.error('Error handling win:', error);
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Player not found' });
    }
    res.status(500).json({ error: 'Failed to process win' });
  }
};

// POST /api/wallet/loss - Handle player loss (deduct bet amount)
const handlePlayerLoss = async (req, res) => {
    console.log("handlePlayerLoss")
  try {
    const { playerId, betAmount, gameId } = req.body;
    
    if (!playerId || !betAmount || !gameId) {
      return res.status(400).json({ error: 'Player ID, bet amount, and game ID are required' });
    }
    
    if (betAmount <= 0) {
      return res.status(400).json({ error: 'Bet amount must be positive' });
    }
    
    // Check if player has sufficient balance
    const currentPlayer = await prisma.player.findUnique({
      where: { id: parseInt(playerId) }
    });
    
    if (!currentPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    if (currentPlayer.balance < parseFloat(betAmount)) {
      return res.status(400).json({ error: 'Insufficient balance' });
    }
    
    const player = await prisma.player.update({
      where: { id: parseInt(playerId) },
      data: {
        balance: {
          decrement: parseFloat(betAmount)
        }
      }
    });
    
    // Log the transaction
    console.log(`Player ${playerId} lost ${betAmount} in game ${gameId}. New balance: ${player.balance}`);
    
    res.json({ 
      success: true, 
      newBalance: player.balance, 
      betAmount: parseFloat(betAmount),
      message: 'Bet amount deducted from balance successfully' 
    });
  } catch (error) {
    console.error('Error handling loss:', error);
    res.status(500).json({ error: 'Failed to process loss' });
  }
};

// POST /api/wallet/batch-loss - Handle multiple players loss
const handleBatchPlayerLoss = async (req, res) => {
    console.log("handleBatchPlayerLoss")
  try {
    const { players, betAmount, gameId } = req.body;
    
    if (!players || !Array.isArray(players) || !betAmount || !gameId) {
      return res.status(400).json({ error: 'Players array, bet amount, and game ID are required' });
    }
    
    if (betAmount <= 0) {
      return res.status(400).json({ error: 'Bet amount must be positive' });
    }
    
    const results = [];
    const errors = [];
    
    for (const player of players) {
      try {
        const { playerId, numberOfBoards = 1 } = player;
        const totalBetAmount = parseFloat(betAmount) * numberOfBoards;
        
        // Check if player has sufficient balance
        const currentPlayer = await prisma.player.findUnique({
          where: { id: parseInt(playerId) }
        });
        
        if (!currentPlayer) {
          errors.push({ playerId, error: 'Player not found' });
          continue;
        }
        
        if (currentPlayer.balance < totalBetAmount) {
          errors.push({ playerId, error: 'Insufficient balance' });
          continue;
        }
        
        const updatedPlayer = await prisma.player.update({
          where: { id: parseInt(playerId) },
          data: {
            balance: {
              decrement: totalBetAmount
            }
          }
        });
        
        results.push({
          playerId: parseInt(playerId),
          newBalance: updatedPlayer.balance,
          deductedAmount: totalBetAmount,
          numberOfBoards
        });
        
        console.log(`Player ${playerId} lost ${totalBetAmount} (${numberOfBoards} boards) in game ${gameId}. New balance: ${updatedPlayer.balance}`);
      } catch (error) {
        errors.push({ playerId: player.playerId, error: error.message });
      }
    }
    
    res.json({ 
      success: true, 
      results,
      errors,
      message: `Processed ${results.length} players successfully, ${errors.length} errors` 
    });
  } catch (error) {
    console.error('Error handling batch loss:', error);
    res.status(500).json({ error: 'Failed to process batch loss' });
  }
};

// POST /api/wallet/update-balance - Manually update player balance (admin)
const updatePlayerBalance = async (req, res) => {
    console.log("updatePlayerBalance")
    try {
    const { playerId, newBalance } = req.body;
    
    if (!playerId || newBalance === undefined) {
      return res.status(400).json({ error: 'Player ID and new balance are required' });
    }
    
    if (newBalance < 0) {
      return res.status(400).json({ error: 'Balance cannot be negative' });
    }
    
    const player = await prisma.player.update({
      where: { id: parseInt(playerId) },
      data: {
        balance: parseFloat(newBalance)
      }
    });
    
    console.log(`Player ${playerId} balance updated to ${newBalance}`);
    
    res.json({ 
      success: true, 
      newBalance: player.balance,
      message: 'Balance updated successfully' 
    });
  } catch (error) {
    console.error('Error updating balance:', error);
    if (error.code === 'P2025') {
      return res.status(404).json({ error: 'Player not found' });
    }
    res.status(500).json({ error: 'Failed to update balance' });
  }
};

module.exports = {
  getPlayerBalance,
  handlePlayerWin,
  handlePlayerLoss,
  handleBatchPlayerLoss,
  updatePlayerBalance
};
