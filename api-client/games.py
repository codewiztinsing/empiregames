import requests
import json
from typing import Dict, Any, List


def get_all_games(base_url: str) -> Dict[str, Any]:
    """Get all games from the API."""
    url = f"{base_url}/api/v1/games"
    try:
        response = requests.get(url)
        return response.json()
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


def get_game_by_id(base_url: str, game_id: int) -> Dict[str, Any]:
    """Get a specific game by ID."""
    url = f"{base_url}/api/v1/games/{game_id}"
    try:
        response = requests.get(url)
        return response.json()
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


def create_game(base_url: str, bet_amount: int, max_players: int = 10) -> Dict[str, Any]:
    """Create a new game."""
    url = f"{base_url}/api/v1/games"
    payload = {
        "betAmount": bet_amount,
        "maxPlayers": max_players
    }
    print(payload)
    try:
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        print(response.json())
        print(response.status_code)
        return response.json()
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


def update_game(base_url: str, game_id: int, name: str = None, status: str = None, max_players: int = None) -> Dict[str, Any]:
    """Update an existing game."""
    url = f"{base_url}/api/v1/games/{game_id}"
    payload = {}
    
    if name is not None:
        payload["name"] = name
    if status is not None:
        payload["status"] = status
    if max_players is not None:
        payload["maxPlayers"] = max_players
    
    print(payload)
    try:
        response = requests.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        print(response.json())
        print(response.status_code)
        return response.json()
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


def delete_game(base_url: str, game_id: int) -> Dict[str, Any]:
    """Delete a game by ID."""
    url = f"{base_url}/api/v1/games/{game_id}"
    print(url)
    try:
        response = requests.delete(url)
        return response.json()
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
    base_url = "http://localhost:5000"
    
    # Create a new game
    new_game = create_game(base_url, 100, 8)
    print("Created game:", new_game)
    
    # Get all games
    all_games = get_all_games(base_url)
    print("All games:", all_games)
    
    # If game was created successfully, test other operations
    if "id" in new_game:
        game_id = new_game["id"]
        
        # Get specific game
        game = get_game_by_id(base_url, game_id)
        print("Game by ID:", game)
        
        # Update game
        updated_game = update_game(base_url, game_id, name="Updated Test Game", status="active")
        print("Updated game:", updated_game)
        
      