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
    



def get_user_phone(user_id):
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}")
    print("phone number response = ",response.json())
    if response.status_code == 200:
        return response.json().get("phone")
    else:
        return None
    
def verify_receipt(message,paymentMethod,session_id):
    """
    Verify a receipt by reference number
    
    Args:
        message (str): The message to verify
        
    Returns:
        dict: Response from the verification endpoint
    """
    manual_pay_url = config("MANUAL_BASE_URL")
    print("manual payment url")
    callbackurl = BACK_URL +  "/api/v1/wallet/manual/callback/success/"
   
    print("callbackurl = ",callbackurl)
    errorUrl = BACK_URL +  "/api/v1/wallet/manual/callback/error/"
    print("errorUrl = ",errorUrl)
    url = f"{manual_pay_url}receipts/verify/"
    data = {"message": message,"callbackurl":callbackurl,"errorUrl":errorUrl,"paymentMethod":paymentMethod,"session_id":session_id}    
    try:
        response = requests.post(url, json=data)
        print("response = ",response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("error = ",e)
        return {"error": f"Request failed: {str(e)}"}



def get_game_type():
    response = requests.get(f"{BACK_URL}/api/v1/game/game-types/")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def create_withdrawal_request(telegram_id, amount):
    response = requests.post(f"{BACK_URL}/api/v1/wallet/withdrawal/request/", json={"telegram_id": telegram_id, "amount": amount})
    if response.status_code == 200:
        return response.json()
    else:
        return None

   

def get_manual_deposits_settings():
    try:
        response = requests.get(f"{BACK_URL}/api/v1/wallet/manual/deposits/settings/")
        if response.status_code == 200:
            return response.json().get("minimum_deposit_amount", 50)  # Default to 50 if not found
        else:
            return 50  # Default minimum deposit amount
    except Exception as e:
        print(f"Error fetching deposit settings: {e}")
        return 50  # Default minimum deposit amount

def get_manual_withdrawals_settings():
    try:
        response = requests.get(f"{BACK_URL}/api/v1/wallet/manual/withdrawals/settings/")
        if response.status_code == 200:
            return response.json().get("minimum_withdrawal_amount", 20)  # Default to 20 if not found
        else:
            return 20  # Default minimum withdrawal amount
    except Exception as e:
        print(f"Error fetching withdrawal settings: {e}")
        return 20  # Default minimum withdrawal amount

def get_withdrawal_fee():
    try:
        response = requests.get(f"{BACK_URL}/api/v1/wallet/manual/withdrawals/settings/")
        if response.status_code == 200:
            return response.json().get("withdrawal_fee", 0)  # Default to 0 if not found
        else:
            return 0  # Default withdrawal fee
    except Exception as e:
        print(f"Error fetching withdrawal fee: {e}")
        return 0  # Default withdrawal fee



