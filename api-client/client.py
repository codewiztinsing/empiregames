data = {

  "amount": 51.75,
            "currency": "ETB",
            "tx_ref": "1234567890",
            "phone_number": "251912345678",
            "first_name":"alako",
            "last_name":"abiyo",
            "email":"alako@gmail.com"
}

import requests

url = "http://127.0.0.1:8000/api/v1/wallet/chapa/create-session"

response = requests.post(url, json=data)

print(response.status_code)