const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/v1/dashboard/stats - Get dashboard statistics
const getDashboardStats = async (req, res) => {
  try {
    // Get total number of players
    const totalPlayers = await prisma.player.count();
    
    // Get total number of games
    const totalGames = await prisma.game.count();

    // get players joined in today
    const playersJoinedToday = await prisma.player.count({
      where: {
        joinedAt: {
          gte: new Date(new Date().setHours(0, 0, 0, 0)),
          lte: new Date(new Date().setHours(23, 59, 59, 999))
        }
      }
    });

    // total playes 
    
    // Get games by status
    const gamesByStatus = await prisma.game.groupBy({
      by: ['status'],
      _count: {
        id: true
      }
    });
    
    // Get total balance across all players
    const totalBalance = await prisma.player.aggregate({
      _sum: {
        balance: true
      }
    });
    
    // Get recent games (last 10)
    const recentGames = await prisma.game.findMany({
      take: 10,
      orderBy: {
        createdAt: 'desc'
      },
      include: {
        winner: {
          select: {
            id: true,
            username: true
          }
        },
        players: {
          select: {
            id: true,
            username: true
          }
        }
      }
    });
    
    // Get top players by balance
    const topPlayers = await prisma.player.findMany({
      take: 5,
      orderBy: {
        balance: 'desc'
      },
      select: {
        id: true,
        username: true,
        balance: true,
        wonGames: {
          select: {
            id: true
          }
        }
      }
    });

    // Transform the data to include won games count
    const topPlayersWithCount = topPlayers.map(player => ({
      id: player.id,
      username: player.username,
      balance: player.balance,
      wonGamesCount: player.wonGames.length
    }));


    // get deposits
    const deposits = await prisma.deposit.findMany();

    // get withdrawals
    const withdrawals = await prisma.withdrawal.findMany();

    // get total deposits
    const totalDeposits = await prisma.deposit.aggregate({
      _sum: {
        amount: true
      }
    });

    // get total withdrawals
    const totalWithdrawals = await prisma.withdrawal.aggregate({
      _sum: {
        amount: true
      }
    });
    
    // Format the response
    const stats = {
      totalPlayers,
      totalGames,
      playersJoinedToday,
      totalBalance: totalBalance._sum.balance || 0,
      gamesByStatus: gamesByStatus.reduce((acc, item) => {
        acc[item.status] = item._count.id;
        return acc;
      }, {}),
      recentGames,
    topPlayers: topPlayersWithCount,
      deposits: deposits.length,
      withdrawals: withdrawals.length,
      totalDeposits: totalDeposits._sum.amount || 0,
      totalWithdrawals: totalWithdrawals._sum.amount || 0
    };
    
    res.json(stats);
  } catch (error) {
    console.error('Dashboard stats error:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard statistics' });
  }
};

module.exports = {
  getDashboardStats
};
