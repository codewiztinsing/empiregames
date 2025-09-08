data = {
  "event": "payout.success",
  "type": "Payout",
  "mode": "live",
  "account_name": None,
  "account_number": "251991221912",
  "bank_id": 855,
  "bank_name": "telebirr",
  "amount": "48.50",
  "charge": "1.50",
  "currency": "ETB",
  "status": "success",
  "reference": "1a5DEOKrBJKi84tnxdZe",
  "chapa_reference": "CTtsz9VUdSaMHB",
  "bank_reference": "CI85PCCS7V",
  "created_at": "2025-09-08T19:11:27.000000Z",
  "updated_at": "2025-09-08T19:11:28.000000Z"
}

import requests

url = "https://wowliyubingo.com/api/v1/webhooks/"

response = requests.post(url, json=data)

print(response.json())