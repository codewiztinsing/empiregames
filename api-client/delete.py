import requests
import json
from typing import Dict, Any


def delete_user(base_url: str, telegram_id: str) -> Dict[str, Any]:
    """
    Delete a user by telegram ID.
    
    Args:
        base_url: The base URL of the API
        telegram_id: The telegram ID of the user to delete
    
    Returns:
        Dict containing success status or error information
    """
    url = f"{base_url}/api/v1/users/{telegram_id}"

    print("url = ",url)
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 204:
            return {
                "success": True,
                "message": "User deleted successfully",
                "status_code": response.status_code
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": "User not found",
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Failed to delete user"),
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
    print(delete_user("http://localhost:5000", "1234567890"))
