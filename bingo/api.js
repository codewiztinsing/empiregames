const axios = require('axios');
const dotenv = require('dotenv');
dotenv.config();

const gameWinWallet = async (player,bet_amount,win_amount)=>{
  const current_game = await getCurrentGame(bet_amount)
  const game_id = current_game.game_id
  const data = {
      player,
      win_amount ,
      game_id
  };

  console.log("data in gameWinWallet",data)

  console.log("data",data)
  if(!data.player || !data.win_amount || !data.game_id) return null;
  
  try{
    const backUrl = process.env.BACK_URL
    const winUrl = backUrl + 'game/win-game/'
    
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
    const backUrl = process.env.BACK_URL
    const balanceUrl = backUrl + 'balance/?user_id=' + playerId
    const response = await fetch(balanceUrl, {
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


const getCurrentGame = async (betAmount)=>{
  const backUrl = process.env.BACK_URL
  
  const currentGameUrl = backUrl + 'game/next-game'
  console.log("currentGameUrl",currentGameUrl)
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
  const current_game = await getCurrentGame(betAmount)
  const game_id = current_game.game_id
 
  const data = {
      players: players,
      bet_amount: betAmount,
      game_id:game_id
  };

  try{
      if(!data.players) return null;
      const backUrl = process.env.BACK_URL
      const lossUrl = backUrl + 'game/join-game/'
      console.log("lossUrl",lossUrl)
      await axios.post(lossUrl,data)
      .then(res=>{
          console.log("gameLossWallet res",res.data)
      })
  }catch(e){
    console.log("gameLossWallet error")
  }
  
}



const updateLastGame = async (roomId)=>{
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
  const backUrl = process.env.BACK_URL
  const gameSettingsUrl = backUrl + 'game/game-settings/'
  const response = await axios.get(gameSettingsUrl)
  const data = response.data;
  return data;
}



  
  
  module.exports = {
    gameWinWallet,
    checkBalance,
    gameLossWallet,
    updateLastGame,
    getGameSettings
  };
  