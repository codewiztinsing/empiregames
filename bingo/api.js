const axios = require('axios');

const gameWinWallet = async (playerId,amount,gameId)=>{
  const data = {
      playerId,
      amount ,
      gameId
  };
  if(!data.playerId || !data.amount || !data.gameId) return null;
  
  try{
      const winUrl = 'https://api.bilenbingo.com/payments/win/'
      
    
     const res=  await axios.post(winUrl,data)
              .then(res=>{
                  console.log("gameWinWallet res",res.data)
                  return res.data
              })
     
  }catch(e){
    console.log("gameWinWallet error",e)
  }
  
} 


const checkBalance = async (playerId) => {
  try {
    const response = await fetch(`${process.env.API_URL}/balance/?user_id=${playerId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch balance');
    }

    const data = await response.json();
    return data.balance;

  } catch (error) {
    console.error('Error checking balance:', error);
    throw error;
  }
};

const gameLossWallet = async (players,betAmount,gameId)=>{
    
  const data = {
      players: players,
      betAmount: betAmount,
      gameId:gameId
  };
  try{
      if(!data.players) return null;
    console.log("data = ",data)
      const lossUrl = 'https://api.bilenbingo.com/payments/loss/'
      await axios.post(lossUrl,data)
      .then(res=>{
          console.log("gameLossWallet res",res.data)
      })
  }catch(e){
    console.log("gameLossWallet error")
  }
  
}



  
  
  module.exports = {
    gameWinWallet,
    checkBalance,
    gameLossWallet
  };
  