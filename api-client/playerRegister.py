import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PlayerRegisterClient:
    """Client for player registration operations"""
    
    def __init__(self, base_url: str):
        """
        Initialize the player register client
        
        Args:
            base_url: The base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def register_player(self, telegram_id: int, username: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new player
        
        Args:
            telegram_id: The player's Telegram ID
            username: The player's username
            phone: The player's phone number (optional)
            
        Returns:
            Dict containing the registration response
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/v1/users/"
        
        data = {
            "telegramId": telegram_id,
            "username": username,
            "phoneNumber": phone
        }
        
       
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Player registered successfully: {telegram_id}")
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to register player {telegram_id}: {e}")
            raise
    
    def check_player_exists(self, telegram_id: int) -> bool:
        """
        Check if a player exists by telegram ID
        
        Args:
            telegram_id: The player's Telegram ID
            
        Returns:
            bool: True if player exists, False otherwise
        """
        url = f"{self.base_url}/api/v1/users/{telegram_id}/"
        
        try:
            response = self.session.get(url)
            return response.status_code == 200
            
        except requests.RequestException as e:
            logger.error(f"Failed to check player existence {telegram_id}: {e}")
            return False
    
    def get_player_info(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get player information by telegram ID
        
        Args:
            telegram_id: The player's Telegram ID
            
        Returns:
            Dict containing player information or None if not found
        """
        url = f"{self.base_url}/api/v1/users/{telegram_id}/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get player info {telegram_id}: {e}")
            return None
    
    def update_player_phone(self, telegram_id: int, phone: str) -> Dict[str, Any]:
        """
        Update player's phone number
        
        Args:
            telegram_id: The player's Telegram ID
            phone: The new phone number
            
        Returns:
            Dict containing the update response
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/v1/users/{telegram_id}/"
        
        data = {"phone": phone}
        
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Player phone updated successfully: {telegram_id}")
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to update player phone {telegram_id}: {e}")
            raise


# Factory function for easy client creation
def create_player_register_client(base_url: str) -> PlayerRegisterClient:
    """
    Create a PlayerRegisterClient instance
    
    Args:
        base_url: The base URL of the API server
        
    Returns:
        PlayerRegisterClient instance
    """
    return PlayerRegisterClient(base_url)



if __name__ == "__main__":
    client = create_player_register_client("http://localhost:5000")
    print(client.register_player(1464395536, "abdul", "1234567891"))
   