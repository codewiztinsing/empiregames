import requests
import random
BASE_URL = "http://localhost:8000/api/v1/users"

def test_register_without_referred():
    data = {
        "username": f"testuser{random.randint(1, 1000)}",
        "phone": str(random.randint(1000000000, 9999999999)),
        "telegram_id": str(random.randint(1000000000, 9999999999)),
        "password": "testpassword1",
        "referred_by": None,
        "email": "testuser1@gmail.com"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print("Register without referred_by:")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    print("-" * 40)

def test_register_with_referred(referred_telegram_id):
    data = {
        "username": f"testuser{random.randint(1, 1000)}",
        "phone": str(random.randint(1000000000, 9999999999)),
        "telegram_id": str(random.randint(1000000000, 9999999999)),
        "password": "testpassword2",
        "referred_by": referred_telegram_id,
        "email": "testuser2@gmail.com"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print("Register with referred_by:")
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    print("-" * 40)

if __name__ == "__main__":
    # First, register a user without referral to get a valid telegram_id for referral
    test_register_without_referred()
    # Use the telegram_id of the first user as the referrer for the second user
    test_register_with_referred("tg_1001")
