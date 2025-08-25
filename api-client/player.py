import requests
from typing import Dict, Any, Optional
import json

class PlayerRegistrationClient:
    """Client for handling player registration with the bingo game API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the player registration client.
        
        Args:
            base_url: The base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def register_player(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new player.
        
        Args:
            player_data: Dictionary containing player registration data
                Required fields: username, password, email
                Optional fields: first_name, last_name, phone
        
        Returns:
            Dictionary containing registration response
        
        Raises:
            requests.exceptions.RequestException: For network-related errors
            ValueError: For invalid response data
        """
        url = f"{self.base_url}/api/players/register"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.post(
                url,
                json=player_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException("Registration request timed out")
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException("Failed to connect to registration server")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from server")
    
    def check_username_availability(self, username: str) -> bool:
        """
        Check if a username is available for registration.
        
        Args:
            username: The username to check
        
        Returns:
            True if username is available, False otherwise
        """
        url = f"{self.base_url}/api/players/check-username"
        
        params = {'username': username}
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get('available', False)
            
        except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError):
            # If we can't check availability, assume it's not available
            return False
    
    def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """
        Verify player email address using verification token.
        
        Args:
            verification_token: The email verification token
        
        Returns:
            Dictionary containing verification response
        """
        url = f"{self.base_url}/api/players/verify-email"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {'token': verification_token}
        
        response = self.session.post(
            url,
            json=data,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """
        Resend verification email to player.
        
        Args:
            email: The player's email address
        
        Returns:
            Dictionary containing response
        """
        url = f"{self.base_url}/api/players/resend-verification"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {'email': email}
        
        response = self.session.post(
            url,
            json=data,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Example of how to use the PlayerRegistrationClient
    client = PlayerRegistrationClient("http://localhost:5000")
    
    # Check if username is available
    if client.check_username_availability("new_player"):
        # Register new player
        player_data = {
            "username": "new_player",
            "password": "secure_password123",
            "email": "player@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }
        
        try:
            result = client.register_player(player_data)
            print("Registration successful:", result)
        except requests.exceptions.RequestException as e:
            print("Registration failed:", e)
    else:
        print("Username not available")
    
    client.close()
