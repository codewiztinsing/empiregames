import requests

url = "http://127.0.0.1:8000/api/v1/wallet/manual/callback/cbe/success/"
payload = {
    "session_id": "5398ce5a-cb4d-48d0-bc6c-f222c3d0a8ec",
    "status": "success",
    "message": "Transaction verified successfully",
    "data": {
        "Customer Name": "TINSAE ALAKO ABIYO",
        "Receiver": "AZEB BEHAILU MEKONEN",
        "Payer": "TINSAE ALAKO ABIYO",
        "Payment Date & Time": "10/15/2025, 11:49:00 AM",
        "Transferred Amount": "10.00 ETB",
        "VAT": "8 ETB",
        "Total Debited": "8 ETB",
        "VAT Receipt No:": "FT252888G5X9"
    }
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response Body:", response.text)
