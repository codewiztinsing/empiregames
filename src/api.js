const checkPlayerBalance = async (playerId) => {
  try {
    const response = await fetch(`${process.env.API_URL}/balance/?user_id=${playerId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.balance
  } catch (error) {
    console.error('Error checking balance:', error);
  }
};