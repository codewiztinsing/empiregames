const axios = require('axios');
const dotenv = require('dotenv');
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
dotenv.config();

const gameWinWallet = async (playerId,bet_amount,win_amount)=>{
  console.log("playerId",playerId)
  console.log("bet_amount",bet_amount)
  console.log("win_amount",win_amount)
  const player = await prisma.player.update({
    where: {
      id: playerId
    },
    data: {
      balance: {
        increment: win_amount
      }
    }
  });
  return player.balance;
 
  
} 


const checkBalance = async (playerId) => {
  console.log("playerId",playerId)
  console.log("checkBalance")
  const player = await prisma.player.findUnique({
    where: {
      id: playerId
    }
  });
  return player.balance;
  
  
};


const getCurrentGame = async (betAmount)=>{
  const backUrl = process.env.BACK_URL
  const currentGameUrl = backUrl + 'game/next-game'
  const params = {
    params: {
      bet_amount: `${betAmount}`
    }
  }
  const response = await axios.get(currentGameUrl, params)
  const data = response.data;
  return data;
}


const gameLossWallet = async (players,betAmount)=>{
  console.log("players ",players)
  console.log("betAmount ",betAmount)
  console.log("gameLossWallet")


  try {
    
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
        console.log("currentPlayer",currentPlayer)
        
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

        console.log("updatedPlayer",updatedPlayer)
        
        results.push({
          playerId: parseInt(playerId),
          newBalance: updatedPlayer.balance,
          deductedAmount: totalBetAmount,
          numberOfBoards
        });
        
        console.log(`Player ${playerId} lost ${totalBetAmount} (${numberOfBoards} boards) in game ${game_id}. New balance: ${updatedPlayer.balance}`);
      } catch (error) {
        errors.push({ playerId: player.playerId, error: error.message });
      }
    }
    
    await prisma.$disconnect();
    console.log("results",results)
    console.log("errors",errors)
    
    return { 
      success: true, 
      results,
      errors,
      message: `Processed ${results.length} players successfully, ${errors.length} errors` 
    };
  } catch (error) {
    console.error('Error handling batch loss:', error);
    throw error;
  }
}



const updateLastGame = async (roomId)=>{
  console.log("roomId",roomId)
  console.log("updateLastGame")
  const backUrl = process.env.BACK_URL
  const updateLastGameUrl = backUrl + 'game/update-last-game/'
  const params = {
    params: {
      bet_amount: `${roomId}`
    }
  }
  const response = await axios.get(updateLastGameUrl, params)
  const data = response.data;
  return data;  
}



const getGameSettings = async ()=>{
  console.log("getGameSettings")
  const backUrl = process.env.BACK_URL
  const gameSettingsUrl = backUrl + 'game/game-settings/'
  const response = await axios.get(gameSettingsUrl)
  const data = response.data;
  return data;
}


const fetchBalance = async () => {
  console.log("fetching balance")

  const apiUrl = process.env.REACT_APP_API_URL;
  console.log("apiUrl", apiUrl)

  try {
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };
    const response = await axios.get(`${apiUrl}wallet/player/${queryParams.get('playerId')}`);
  
  
    setBalance(response.data.balance);
    setLoading(false);
  } catch (error) {
    console.error('Error fetching balance:', error);
  }
};

  
  
  module.exports = {
    gameWinWallet,
    checkBalance,
    gameLossWallet,
    updateLastGame,
    getGameSettings,
  };
  