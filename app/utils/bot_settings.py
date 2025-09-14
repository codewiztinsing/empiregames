from utils.helpers import BACK_URL
import requests
from decouple import config


def get_bot_seetings():
    BACK_URL = config('BACK_URL')   
    BOT_TOKEN = config('BOT_TOKEN')
    return {
        "bot_url":BACK_URL,
        "bot_token":BOT_TOKEN,
    }

def initialize_manual_session(amount, session_id, phone_number):
    print("initialize manual session")
    BACK_URL = config('BACK_URL')
    url = f"{BACK_URL}/api/v1/wallet/manual/session/"
    data = {
        "amount": amount,
        "session_id": session_id,
        "phone_number": phone_number,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        print("manual session response = ",response.json())
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to create session: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        print("manual session error = ",e)
        return {"error": f"Request failed: {str(e)}"}



def verify_telebirr_receipt(message,session_id):
    print("verify telebirr receipt")
    BACK_URL = config('BACK_URL')
    MANUAL_API_KEY = config('MANUAL_API_KEY')
    manual_payment_url = config("MANUAL_BASE_URL")
    manual_payment_url = manual_payment_url + "receipts/verify/telebirr/"
    callbackurl = config("BACK_URL") + "/api/v1/wallet/webhook/manual/success/"
    errorUrl = config("BACK_URL") + "/api/v1/wallet/webhook/manual/error/"
    # callbackurl = "https://webhook.site/eb5edb76-4b62-4400-9c67-fcdc7d5bc018"
    # errorUrl = "https://webhook.site/eb5edb76-4b62-4400-9c67-fcdc7d5bc018"
    data = {
        "message": message,
        "session_id": session_id,
        "callbackurl": callbackurl,
        "errorUrl": errorUrl
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": MANUAL_API_KEY
    }
    try:
        response = requests.post(manual_payment_url, json=data, headers=headers)
        print("verify telebirr receipt response = ",response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("verify telebirr receipt error = ",e)
        return {"error": f"Request failed: {str(e)}"}
  


def verify_cbe_receipt(message,session_id):
    print("verify cbe receipt")
    BACK_URL = config('BACK_URL')
    MANUAL_API_KEY = config('MANUAL_API_KEY')
    manual_payment_url = config("MANUAL_BASE_URL")
    manual_payment_url = manual_payment_url + "receipts/verify/cbe/"
    callbackurl = config("BACK_URL") + "/api/v1/wallet/webhook/manual/cbe/success/"
    errorUrl = config("BACK_URL") + "/api/v1/wallet/webhook/manual/error/"
    
    data = {
        "message": message,
        "session_id": session_id,
        "callbackurl": callbackurl ,
        "errorUrl": errorUrl
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": MANUAL_API_KEY
    }
    try:
        response = requests.post(manual_payment_url, json=data, headers=headers)
        print("verify cbe receipt response = ",response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("verify cbe receipt error = ",e)
        return {"error": f"Request failed: {str(e)}"}
    

