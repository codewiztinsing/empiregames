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

def initialize_manual_session(amount, session_id, phone_number,message):
    BACK_URL = config('BACK_URL')
    MANUAL_BASE_URL = config('MANUAL_BASE_URL') + "receipts/verify/"
    session_url = BACK_URL + "/api/v1/wallet/manual/session/"
    callbackurl = BACK_URL + "/api/v1/wallet/manual/callback/success/"
    errorUrl = BACK_URL + "/api/v1/wallet/manual/callback/error/"
    data = {
        "amount":amount,
        "session_id":session_id,
        "phone_number":phone_number,
    }
    response = requests.post(f"{session_url}", json=data)
    if response.status_code == 200:
        data = {"message": message,"callbackurl":callbackurl,"errorUrl":errorUrl,"paymentMethod":"telebirr"}
        response = requests.post(f"{MANUAL_BASE_URL}", json=data)
        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data
            except Exception:
                print("response (non-JSON) = ", response.text)
                return {"ok": True, "raw": response.text}
        else:
            return {"error": "Failed to verify manual session"}
        return response.json()
    else:
        return {"error": "Failed to initialize manual session"}
    return response.json()

