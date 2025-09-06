import requests
from decouple import config

BACK_URL = config("BACK_URL")

def daily_withdraw_limit(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}/daily-withdraw-limit")
    if response.status_code == 200:
        return response.json().get("daily_withdraw_limit",0)
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

# is deposited player
def is_deposited_player(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}/is-deposited")
    if response.status_code == 200:
        return response.json().get("is_deposited")
    else:
        return False
    




    
def verify_receipt(message,paymentMethod):
    """
    Verify a receipt by reference number
    
    Args:
        message (str): The message to verify
        
    Returns:
        dict: Response from the verification endpoint
    """
    manual_pay_url = config("MANUAL_BASE_URL")
    print("manual payment url")
    callbackurl = config("BACK_URL") +  "/api/v1/wallet/webhook/manual/success/"
    print("callbackurl = ",callbackurl)
    errorUrl = config("BACK_URL") +  "/api/v1/wallet/webhook/manual/error/"
    print("errorUrl = ",errorUrl)
    url = f"{manual_pay_url}receipts/verify/"
    data = {"message": message,"callbackurl":callbackurl,"errorUrl":errorUrl,"paymentMethod":paymentMethod}

    
    try:
        response = requests.post(url, json=data)
        print("response = ",response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("error = ",e)
        return {"error": f"Request failed: {str(e)}"}


