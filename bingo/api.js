const axios = require('axios');
const dotenv = require('dotenv');
dotenv.config();

// Helper function to normalize API URLs
const normalizeApiUrl = (baseUrl, endpoint) => {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const apiPrefix = normalizedBase.includes('/api/v1') ? '' : '/api/v1';
  const finalUrl = `${normalizedBase}${apiPrefix}/${endpoint}`;
  console.log(`[URL Normalize] baseUrl: ${baseUrl}, normalizedBase: ${normalizedBase}, apiPrefix: '${apiPrefix}', endpoint: ${endpoint}, finalUrl: ${finalUrl}`);
  return finalUrl;
};

const gameWinWallet = async (player, bet_amount, win_amount, total_players)=>{
  console.log("gameWinWallet called with:", {player, bet_amount, win_amount, total_players});
  const current_game = await getCurrentGame(bet_amount)
  console.log("current_game:", current_game);
  const game_id = current_game.game_id
  const data = {
      player,
      bet_amount,
      win_amount,
      total_players,
      game_id
  };

  console.log("gameWinWallet data:", data);

  if(!data.player || !data.win_amount || !data.game_id) {
    console.log("gameWinWallet validation failed:", {player: data.player, win_amount: data.win_amount, game_id: data.game_id});
    return null;
  }
  
  try{
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    console.log("baseUrl",baseUrl)
    const winUrl = normalizeApiUrl(baseUrl, 'game/win-game/');
    console.log("winUrl",winUrl)
    console.log("Sending POST request to win-game with data:", data);
    await axios.post(winUrl, data)
              .then(res=>{
                  console.log("gameWinWallet res",res.data)
              })
      
     
       
  }catch(e){
    console.log("gameWinWallet error",e)
  }
  
} 


const checkBalance = async (playerId) => {
  try {
    const baseUrl = process.env.REACT_APP_BACK_URL || 'http://localhost:8000';
    const balanceUrl = `${baseUrl}balance/?user_id=${playerId}`;
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
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const currentGameUrl = normalizeApiUrl(baseUrl, 'game/next-game/');
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


const gameLossWallet = async (players, betAmount, totalPlayers = null, fakePlayers = 0)=>{
  const current_game = await getCurrentGame(betAmount)
  console.log("current_game",current_game)
  const game_id = current_game.game_id
 
  const data = {
      players: players,
      bet_amount: betAmount,
      game_id: game_id,
      total_players: totalPlayers,
      fake_players: fakePlayers
  };


  try{
      if(!data.players) return null;
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const lossUrl = normalizeApiUrl(baseUrl, 'game/join-game/');
      console.log("lossUrl",lossUrl)
      console.log("data",data)
      await axios.post(lossUrl,data)
      .then(res=>{
          console.log("gameLossWallet res",res.data)
      })
  }catch(e){
    console.log("gameLossWallet error", e)
  }
  
}







const getGameSettings = async ()=>{
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const gameSettingsUrl = normalizeApiUrl(baseUrl, 'game/game-settings/');
  const response = await axios.get(gameSettingsUrl)
  const data = response.data;
  return data;
}

const getFakePlayerSettings = async ()=>{
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const fakePlayerSettingsUrl = normalizeApiUrl(baseUrl, 'game/fake-player-settings/');
  const response = await axios.get(fakePlayerSettingsUrl)
  const data = response.data;
  return data;
}



  
  
  module.exports = {
    gameWinWallet,
    checkBalance,
    gameLossWallet,
    getGameSettings,
    getFakePlayerSettings
  };
  