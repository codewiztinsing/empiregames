import requests
import json
# from app.utils.helpers import BACK_URL
from decouple import config

API_KEY = config("PROD_SECRET_KEY")
ENCRYPTION_KEY = config("PROD_ENCRYPTION_KEY")
url = "https://api.chapa.co/v1/transaction/initialize"

def initialize_payment(amount, currency, email, first_name, last_name, phone_number, tx_ref):
    print("tx_ref = ",tx_ref)
    payload = {
        "amount": amount,
        "currency": currency,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "tx_ref": tx_ref
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    print("payload = ",payload)
    print("headers = ",headers)
    response = requests.post(url, json=payload, headers=headers)
    return response.json()




def transfer_funds(account_name, account_number, amount, currency, reference, bank_code ):
    url = "https://api.chapa.co/v1/transfers"
    payload = {
        "account_name": account_name,
        "account_number": account_number,
        "amount": amount,
        "currency": currency,
        "reference": reference,
        "bank_code": bank_code
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    print("withdraw funds url = ",url)
    print("withdraw funds payload = ",payload)
    print("withdraw funds headers = ",headers)
    print("withdraw funds = ",response.json())
    return response.json()




def get_available_banks():
    url = "https://api.chapa.co/v1/banks"
    payload = ''
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(url, headers=headers)
    print("get available banks = ",response.json())
    return response.json()


def initialize_chapa_direct_charges(phone_number,amount,tx_ref,first_name,last_name):
    url = "https://api.chapa.co/v1/charges?type=telebirr"
    BACK_URL = config("BACK_URL")
    chapa_session = None
    url = f"{BACK_URL}/api/v1/wallet/chapa/create-session"
    # Data to send
    data = {
        "amount": amount,
        "currency": "ETB",
        "tx_ref": tx_ref,
        "mobile": phone_number
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    # POST request with form data
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        # (amount, currency, email, first_name, last_name, phone_number, tx_ref
        data = {
              "amount": amount,
            "currency": "ETB",
            "tx_ref": tx_ref,
            "phone_number": phone_number,
            "first_name":first_name,
            "last_name":last_name,
            "email":f"{first_name}@gmail.com"

        }
       
        chapa_session = requests.post(url, json=data)
        print("chapa session = ",chapa_session.json())
        return chapa_session.json()
    else:
        return {"error": "Failed to initialize chapa direct charges"}



