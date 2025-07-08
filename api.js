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

const chargePlayers = async (game) => {
  try {
    const response = await fetch(`https://api.bilenbingo.com/payments/charge-players`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        game:game       
      })
    });

    if (!response.ok) {
      throw new Error('Failed to charge players');
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error('Error charging players:', error);
    throw error;
  }
};



  
  
  module.exports = {
    submitWinner,
    checkBalance
  };
  