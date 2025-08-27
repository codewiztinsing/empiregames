import requests
from decouple import config

BACK_URL = config("BACK_URL")

def daily_withdraw_limit(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/wallet/users/{user_id}/daily-withdraw-limit")
    if response.status_code == 200:
        return response.json().get("daily_withdraw_limit")
    else:
        return 0

def numnber_of_game_played(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}/number-of-game-played")
    if response.status_code == 200:
        return response.json().get("number_of_game_played")
    else:
        return 0

def number_of_game_won(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}/number-of-game-won")
    if response.status_code == 200:
        return response.json().get("number_of_game_won")
    else:
        return 0
    


        