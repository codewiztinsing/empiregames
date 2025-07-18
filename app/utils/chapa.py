import requests
import json
from decouple import config

API_KEY = config("PROD_SECRET_KEY")
ENCRYPTION_KEY = config("PROD_ENCRYPTION_KEY")
url = "https://api.chapa.co/v1/transaction/initialize"

def initialize_payment(amount, currency, email, first_name, last_name, phone_number, tx_ref, callback_url, return_url, customization):
    print("tx_ref = ",tx_ref)
    payload = {
        "amount": amount,
        "currency": currency,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url,
        "customization": customization
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
    return response.json()



# if __name__ == "__main__":
#     print(transfer_funds("Alako Abiyo", "0991221912", 1, "ETB", "3241342142sfdd", 855))