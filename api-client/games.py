import requests
import json
from typing import Dict, Any, List

def get_all_players(base_url: str) -> Dict[str, Any]:
    """Get all players from the API."""
    url = f"{base_url}/api/v1/users"
    return requests.get(url).json()

def get_player_by_id(base_url: str, player_id: int) -> Dict[str, Any]:
    """Get a specific player by ID."""
    url = f"{base_url}/api/v1/players/{player_id}"
    return requests.get(url).json()

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


def add_player_to_game(base_url: str, game_id: int, player_id: int) -> Dict[str, Any]:
    """Add a player to a game."""
    url = f"{base_url}/api/v1/games/add-player"
    payload = {
        "gameId": game_id,
        "playerId": player_id
    }
    print(payload)
    return requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}).json()

if __name__ == "__main__":
    base_url = "http://localhost:5000"
    # Get all games
    all_games = get_all_games(base_url)
    # Get all players
    all_players = get_all_players(base_url)
    for game in all_games:
        for player in all_players:
            add_player_to_game(base_url, game["id"], player["id"])

    
 