data ={
  "session_id": "dbe30b2c-425c-447b-8a6e-0076685a6601",
  "status": "success",
  "message": "Transaction verified successfully",
  "data": {
    "Customer Name": "TINSAE ALAKO ABIYO",
    "Receiver": "TAGESE SAMUEL ORJINO",
    "Payer": "TINSAE ALAKO ABIYO",
    "Payment Date & Time": "9/13/2025, 3:21:00 PM",
    "Transferred Amount": "540.00 ETB",
    "VAT": "0 ETB",
    "Total Debited": "0 ETB",
    "VAT Receipt No:": "FT252566PF9D"
  }
}
import requests

url = "http://127.0.0.1:8000/api/v1/wallet/manual/callback/telebirr/success/"
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")