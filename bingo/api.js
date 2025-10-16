const axios = require('axios');
const dotenv = require('dotenv');
dotenv.config();

const gameWinWallet = async (player, bet_amount, win_amount, total_players)=>{
  const current_game = await getCurrentGame(bet_amount)
  const game_id = current_game.game_id
  const data = {
      player,
      bet_amount,
      win_amount,
      total_players,
      game_id
  };

  if(!data.player || !data.win_amount || !data.game_id) return null;
  
  try{
    const backUrl = process.env.BACK_URL
    console.log("backUrl",backUrl)
    const winUrl = backUrl + 'game/win-game/'
    console.log("winUrl",winUrl)
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
  console.log("data",data)


  try{
      if(!data.players) return null;
      const backUrl = process.env.BACK_URL
      const lossUrl = backUrl + 'game/join-game/'
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



const updateLastGame = async (roomId)=>{
  console.log("updateLastGame roomId = ", roomId)
  const backUrl = process.env.BACK_URL
  const updateLastGameUrl = backUrl + 'game/update-last-game/'
  console.log("updateLastGameUrl = ", updateLastGameUrl)
  const response = await axios.get(updateLastGameUrl, { params: { bet_amount: `${roomId}` } })
  console.log("updateLastGame response = ", response.data)
  const data = response.data;
  console.log("updateLastGame data = ", data)
  return data;  
}


const updateGameMetrics = async (betAmount, realPlayers, fakePlayers, totalPlayers, winAmount) => {
  console.log("updateGameMetrics betAmount = ", betAmount)
  console.log("updateGameMetrics realPlayers = ", realPlayers)
  console.log("updateGameMetrics fakePlayers = ", fakePlayers)
  console.log("updateGameMetrics totalPlayers = ", totalPlayers)
  console.log("updateGameMetrics winAmount = ", winAmount)
  try {
    const current = await getCurrentGame(betAmount);
    const game_id = current?.game_id;
    if (!game_id) return null;
    const backUrl = process.env.BACK_URL;
    const url = backUrl + 'game/update-metrics/';
    const payload = {
      game_id,
      bet_amount: betAmount,
      real_players: realPlayers,
      fake_players: fakePlayers,
      total_players: totalPlayers,
      win_amount: winAmount
    };
    await axios.post(url, payload).then(res => {
      console.log('updateGameMetrics res', res.data);
    });
    return true;
  } catch (e) {
    console.log('updateGameMetrics error', e?.message || e);
    return null;
  }
};


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
    getGameSettings,
    updateGameMetrics
  };
  