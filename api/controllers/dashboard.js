const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET /api/v1/dashboard/stats - Get dashboard statistics
const getDashboardStats = async (req, res) => {
  try {
    // Get total number of players
    const totalPlayers = await prisma.player.count();

    const allPromotions = await prisma.promotion.findMany();
    
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

    


    // get deposits (payment sessions)
    const deposits = await prisma.paymentSession.findMany({
      where: { status: 'completed' }
    });

    // get withdrawals (payment requests)
    const withdrawals = await prisma.paymentRequest.findMany({
      where: { status: 'completed' }
    });

    // get total deposits
    const totalDeposits = await prisma.paymentSession.aggregate({
      where: { status: 'completed' },
      _sum: {
        amount: true
      }
    });

    // get total withdrawals
    const totalWithdrawals = await prisma.paymentRequest.aggregate({
      where: { status: 'completed' },
      _sum: {
        amount: true
      }
    });

    // Calculate 30 days ago from now
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    // Get data for last 30 days
    const gamesLast30Days = await prisma.game.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const playersLast30Days = await prisma.player.count({
      where: {
        joinedAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const depositsLast30Days = await prisma.paymentSession.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        },
        status: 'completed'
      }
    });

    const withdrawalsLast30Days = await prisma.paymentRequest.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        },
        status: 'completed'
      }
    });

    const revenueLast30Days = await prisma.paymentSession.aggregate({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        },
        status: 'completed'
      },
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
      allPromotions,
      deposits: deposits.length,
      withdrawals: withdrawals.length,
      totalDeposits: totalDeposits._sum.amount || 0,
      totalWithdrawals: totalWithdrawals._sum.amount || 0,
      gamesLast30Days,
      playersLast30Days,
      depositsLast30Days,
      withdrawalsLast30Days,
      revenueLast30Days 
    };
    
    res.json(stats);
  } catch (error) {
    console.error('Dashboard stats error:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard statistics' });
  }
};

// GET /api/v1/dashboard/stats/recent - Get dashboard recent statistics
const getDashboardRecentStats = async (req, res) => {
  try {
    const { timeRange } = req.query;
    console.log("timeRange ",timeRange);
    // Calculate date range based on timeRange parameter
    let startDate;
    const endDate = new Date();
    
    switch (timeRange) {
      case 'today':
        startDate = new Date();
        startDate.setHours(0, 0, 0, 0);
        break;
      case 'last7days':
        startDate = new Date();
        startDate.setDate(startDate.getDate() - 7);
        break;
      case 'last30days':
      default:
        startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);
        break;
    }

    // Get filtered data based on time range
    const filteredPlayers = await prisma.player.findMany({
      where: {
        joinedAt: {
          gte: startDate,
          lte: endDate
        }
      }
    });

    const filteredGames = await prisma.game.findMany({
      where: {
        createdAt: {
          gte: startDate,
          lte: endDate
        }
      },
      include: {
        players: true
      }
    });

    const filteredDeposits = await prisma.deposit.findMany({
      where: {
        createdAt: {
          gte: startDate,
          lte: endDate
        }
      }
    });

    const filteredWithdrawals = await prisma.withdrawal.findMany({
      where: {
        createdAt: {
          gte: startDate,
          lte: endDate
        }
      }
    });

    // Calculate filtered aggregations
    const filteredTotalDeposits = await prisma.deposit.aggregate({
      where: {
        createdAt: {
          gte: startDate,
          lte: endDate
        }
      },
      _sum: {
        amount: true
      }
    });

    const filteredTotalWithdrawals = await prisma.withdrawal.aggregate({
      where: {
        createdAt: {
          gte: startDate,
          lte: endDate
        }
      },
      _sum: {
        amount: true
      }
    });

    // Get filtered balance for the time period
    const filteredBalance = await prisma.player.aggregate({
      where: {
        joinedAt: {
          gte: startDate,
          lte: endDate
        }
      },
      _sum: {
        balance: true
      }
    });

    // Calculate 30 days ago from now
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    // Get data for last 30 days
    const gamesLast30Days = await prisma.game.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const playersLast30Days = await prisma.player.count({
      where: {
        joinedAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const depositsLast30Days = await prisma.deposit.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const withdrawalsLast30Days = await prisma.withdrawal.count({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        }
      }
    });

    const revenueLast30Days = await prisma.deposit.aggregate({
      where: {
        createdAt: {
          gte: thirtyDaysAgo
        },
        status: 'completed'
      },
      _sum: {
        amount: true
      }
    });

    // Format the filtered response
    const filteredStats = {
      newPlayers: filteredPlayers.length,
      totalGames: filteredGames.length,
      revenue: filteredBalance._sum.balance || 0,
      deposits: filteredDeposits.length,
      withdrawals: filteredWithdrawals.length,
      totalDeposits: filteredTotalDeposits._sum.amount || 0,
      totalWithdrawals: filteredTotalWithdrawals._sum.amount || 0,
      timeRange,
      startDate,
      endDate
    };
    res.json(filteredStats);
  } catch (error) {
    console.error('Dashboard recent stats error:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard recent statistics' });
  }
};


module.exports = {
  getDashboardStats,
  getDashboardRecentStats
};
