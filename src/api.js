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
      console.log(data);
      return data.balance;
   
    } catch (error) {
      console.error('Error checking balance:', error);
      throw error;
    }
  };

  export default checkBalance;