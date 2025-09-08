data = {
  "session_id": "488d7952-3ee3-42e4-8e1e-fefc5f2ae08e",
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
    "total_in_words": "thirty-one birr and zero cent",
    "payment_mode": "telebirr",
    "payment_reason": "Send Money to Registered Customer",
    "payment_channel": "API/App",
    "customer_note": "",
    "amount": 31,
    "transaction_number": "CI84P8MDJW"
  }
}

import requests

url = "http://localhost:8000/api/v1/wallet/manual/callback/success/"

response = requests.post(url, json=data)

print(response.json())