data = {
  "session_id": "9e63df62-d1e4-4cb6-802c-18f219a26f41",
  "status": "success",
  "message": "Transaction verified successfully",
  "data": {
    "payer_name": "alako abiyo ludago",
    "payer_telebirr_no": "2519****1912",
    "payer_account_type": "Individual Customer",
    "credited_party": "ESHETU FEYISSA ABERA",
    "credited_account": "2519****4252",
    "transaction_status": "የከፋይ ስም/Payer Name",
    "invoice_no": "የክፍያ ቀን/Payment date",
    "payment_date": "የክፍያ ዝርዝር/ Invoice details",
    "settled_amount": "የክፍያ ዝርዝር/ Invoice details",
    "service_fee": "0.87 Birr",
    "total_paid": "የክፍያ ዝርዝር/ Invoice details",
    "total_in_words": "fifty-one birr and zero cent",
    "payment_mode": "telebirr",
    "payment_reason": "Send Money to Registered Customer",
    "payment_channel": "API/App",
    "customer_note": "",
    "amount": 51
  }
}

import requests

url = "http://localhost:8000/api/v1/wallet/manual/callback/success/"

response = requests.post(url, json=data)

print(response.json())