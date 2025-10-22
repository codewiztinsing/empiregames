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
    print("is deposited response = ",response.json())
    if response.status_code == 200:
        return response.json().get("is_deposited")
    else:
        return False
    



def get_user_phone(user_id):
    print(f"DEBUG: Getting phone for user_id: {user_id}")
    response = requests.get(f"{BACK_URL}/api/v1/users/{user_id}")
    print("phone number response = ",response.json())
    if response.status_code == 200:
        phone = response.json().get("phone")
        print(f"DEBUG: Retrieved phone number: {phone} (type: {type(phone)})")
        return phone
    else:
        print(f"DEBUG: Failed to get phone for user_id: {user_id}, status: {response.status_code}")
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
    try:
        response = requests.get(f"{BACK_URL}/api/v1/game/game-rooms/")
        if response.status_code == 200:
            data = response.json()
            # Convert game_rooms to game_types format for backward compatibility
            game_rooms = data.get('game_rooms', [])
            game_types = []
            for room in game_rooms:
                game_types.append({
                    'bet_amount': str(room['entry_fee']),
                    'commission': str(room.get('house_edge_percentage', 0)),
                    'id': room['id'],
                    'name': room.get('name', f"Game Room {room['entry_fee']} ETB")
                })
            return {'game_types': game_types}
        else:
            logger.error(f"Failed to fetch game rooms: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching game rooms: {e}")
        return None

