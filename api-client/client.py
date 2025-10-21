import requests
import json
import time
from urllib.parse import quote

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def post_telegram_auth(self, data, headers=None):
        """
        Send a POST request to /api/v1/users/telegram-auth

        :param data: The JSON data to send in the request body.
        :param headers: Optional dictionary of HTTP headers to send.
        :return: Response object from the requests library.
        """
        url = f"{self.base_url}/api/v1/users/telegram-auth"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        response = requests.post(url, json=data, headers=default_headers)
        
        return response

    def post_telegram_register(self, data, headers=None):
        """
        Send a POST request to /api/v1/users/telegram-register

        :param data: The JSON data to send in the request body.
        :param headers: Optional dictionary of HTTP headers to send.
        :return: Response object from the requests library.
        """
        url = f"{self.base_url}/api/v1/users/telegram-register"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        response = requests.post(url, json=data, headers=default_headers)
        
        return response

    def create_test_telegram_data(self, telegram_id=123456789, first_name="John", last_name="Doe", username="johndoe"):
        """
        Create test Telegram data with proper structure
        Note: This creates test data that will fail validation but has correct structure
        """
        current_time = int(time.time())
        
        # Create user data
        user_data = {
            "id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "language_code": "en",
            "is_premium": False,
            "photo_url": None
        }
        
        # Create init_data string (URL encoded)
        user_json = json.dumps(user_data, separators=(',', ':'))
        init_data_parts = [
            f"user={quote(user_json)}",
            "chat_instance=-123456789",
            "chat_type=sender",
            f"auth_date={current_time}",
            "hash=test_hash_12345"  # This will fail validation but has correct structure
        ]
        init_data = "&".join(init_data_parts)
        
        return {
            "init_data": init_data,
            "user": user_data,
            "auth_date": current_time,
            "hash": "test_hash_12345"
        }

# Example usage:
client = APIClient("http://localhost:8000")

# Create test data with proper structure
telegram_auth_data = client.create_test_telegram_data(
    telegram_id=123456789,
    first_name="John",
    last_name="Doe", 
    username="johndoe"
)

print("Sending Telegram Auth Data:")
print(json.dumps(telegram_auth_data, indent=2))

# Test telegram auth
resp = client.post_telegram_auth(telegram_auth_data)
print(f"\nTelegram Auth Response: {resp.status_code}")
print(f"Response: {resp.json()}")

# Create registration data
telegram_register_data = client.create_test_telegram_data(
    telegram_id=987654321,
    first_name="Jane",
    last_name="Smith",
    username="janesmith"
)
telegram_register_data["phone"] = "+251912345678"
telegram_register_data["referred_by"] = "123456789"

print(f"\nSending Telegram Register Data:")
print(json.dumps(telegram_register_data, indent=2))

# Test telegram register
resp = client.post_telegram_register(telegram_register_data)
print(f"\nTelegram Register Response: {resp.status_code}")
print(f"Response: {resp.json()}")
