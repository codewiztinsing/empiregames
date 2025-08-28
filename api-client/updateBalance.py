import requests
import json
from typing import Dict, Any

def update_player_balance(base_url: str, telegram_id: str, new_balance: float) -> Dict[str, Any]:
    """
    Update a player's balance
    
    Args:
        base_url: The base URL of the API server
        telegram_id: The telegram ID of the player
        new_balance: The new balance amount
        
    Returns:
        Dict containing success status, data, and message
    """
    url = f"{base_url}/api/v1/users/{telegram_id}/"
    payload = {
        "balance": new_balance
    }
    
    try:
        response = requests.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "message": "Balance updated successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update balance: {response.text}",
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}",
            "status_code": None
        }


if __name__ == "__main__":
    # Example usage
    base_url = "http://localhost:5000"
    telegram_id = 1464395537
    
 
    # Update balance
    update_result = update_player_balance(base_url, telegram_id, 100.50)
    print("Update result:", update_result)
