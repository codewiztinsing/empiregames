import requests
import json
import string
import random
from typing import Dict, Optional, Any

def random_phone_number():
    return ''.join(random.choices(string.digits, k=10))

def random_telegram_id():
    return ''.join(random.choices(string.digits, k=10))

def random_username():
    return ''.join(random.choices(string.ascii_letters, k=10))

def register_user(base_url: str, name: str, game_id: int) -> Dict[str, Any]:
    """
    Register a new user with the API.
    
    Args:
        base_url: The base URL of the API (e.g., 'http://localhost:3000')
        name: The name of the user to register
        game_id: The ID of the game to associate with the user
    
    Returns:
        Dict containing the registered user data or error information
    """
    url = f"{base_url}/api/users"
    
    payload = {
        "name": name,
        "gameId": game_id
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            return {
                "success": True,
                "data": response.json(),
                "message": "User registered successfully"
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Registration failed"),
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": None
        }


def get_user(base_url: str, username: str) -> Dict[str, Any]:
    """
    Get user information by ID.
    
    Args:
        base_url: The base URL of the API
        username: The username of the user to retrieve
    
    Returns:
        Dict containing the user data or error information
    """
    url = f"{base_url}/api/users/{telegramId}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Failed to fetch user"),
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": None
        }


def get_all_users(base_url: str) -> Dict[str, Any]:
    url = f"{base_url}/api/v1/users"
    print(url)
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": "Failed to fetch users",
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": None
        }

def create_user(base_url: str, username: str, telegramId: str, phoneNumber: str, password: str) -> Dict[str, Any]:
    url = f"{base_url}/api/v1/users"
    payload = {
        "username": username,
        "telegramId": telegramId,
        "phoneNumber": phoneNumber,
        "password": password
    }
    print(payload)
    try:
        response = requests.post(url,data=json.dumps(payload),headers={"Content-Type": "application/json"})
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

def delete_user(base_url: str, username: str) -> Dict[str, Any]:
    url = f"{base_url}/api/v1/users/{username}"
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


def login(base_url: str, username: str, password: str) -> Dict[str, Any]:
    url = f"{base_url}/api/v1/auth/login"
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        return {
            "success": True,
            "data": response.json(),
            "message": "Login successful"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "status_code": None
        }


def update_user(base_url: str, username: str, password: str) -> Dict[str, Any]:
    url = f"{base_url}/api/v1/users/{username}"
    payload = {
        "password": password
    }
    try:
        response = requests.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        return {
            "success": True,
            "data": response.json(),
            "message": "User updated successfully"
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
    # base_url = "https://server.akerbingo.com"
    base_url = "http://localhost:5000"
    username = random_username()
    telegramId = random_telegram_id()
    phoneNumber = random_phone_number()
    password = "123456"


    print(create_user(base_url, username, telegramId, phoneNumber, password))
    user = login(base_url, username, password)
    print(user["data"])
   