import requests
from typing import Dict, Any, List


def get_player_balance(base_url: str, player_id: int) -> Dict[str, Any]:
    """Get player balance by ID."""
    url = f"{base_url}/api/v1/wallet/player/{player_id}"
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


def handle_player_win(base_url: str, player_id: int, amount: float) -> Dict[str, Any]:
    """Handle player win - add amount to balance."""
    url = f"{base_url}/api/v1/wallet/win"
    data = {
        "playerId": player_id,
        "amount": amount
    }
    try:
        response = requests.post(url, json=data)
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


def handle_player_loss(base_url: str, player_id: int, amount: float) -> Dict[str, Any]:
    """Handle player loss - subtract amount from balance."""
    url = f"{base_url}/api/v1/wallet/loss"
    data = {
        "playerId": player_id,
        "amount": amount
    }
    try:
        response = requests.post(url, json=data)
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


def handle_batch_player_loss(base_url: str, player_losses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle batch player losses."""
    url = f"{base_url}/api/v1/wallet/batch-loss"
    data = {
        "playerLosses": player_losses
    }
    try:
        response = requests.post(url, json=data)
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


def update_player_balance(base_url: str, player_id: int, new_balance: float) -> Dict[str, Any]:
    """Update player balance (admin function)."""
    url = f"{base_url}/api/v1/wallet/update-balance"
    data = {
        "playerId": player_id,
        "newBalance": new_balance
    }
    try:
        response = requests.post(url, json=data)
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
    
    # Get player balance
    balance = get_player_balance(base_url, 1)
    print("Player balance:", balance)
    
    # Handle player win
    win_result = handle_player_win(base_url, 1, 100.0)
    print("Player win result:", win_result)
    
    # Handle player loss
    loss_result = handle_player_loss(base_url, 1, 50.0)
    print("Player loss result:", loss_result)
    
    # Handle batch player losses
    batch_losses = [
        {"playerId": 1, "amount": 25.0},
        {"playerId": 2, "amount": 30.0}
    ]
    batch_result = handle_batch_player_loss(base_url, batch_losses)
    print("Batch loss result:", batch_result)
    
    # Update player balance (admin)
    update_result = update_player_balance(base_url, 1, 500.0)
    print("Update balance result:", update_result)
