const axios = require('axios');

const submitWinner = async (game) => {
    try {
     
      console.log("game = ",game)
  
  
  
  
    } catch (error) {
      console.error('Error submitting winner:', error);
     
    }
  };


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
          console.log("gameLossWallet res")
      })
  }catch(e){
    console.log("gameLossWallet error")
  }
  
}



  
  
  module.exports = {
    submitWinner,
    checkBalance,
    gameLossWallet
  };
  