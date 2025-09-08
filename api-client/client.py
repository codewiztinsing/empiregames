data = {
  "session_id": "4163c848-1d42-4f2f-ba0d-d0df59dfae6a",
  "status": "success",
  "message": "Transaction verified successfully",
  "data": {
    "payer_name": "alako abiyo ludago",
    "payer_telebirr_no": "2519****1912",
    "payer_account_type": "Individual Customer",
    "credited_party": "CHAPA FINANCIAL TECHNOLOGY SHARE COMPANY",
    "credited_account": "500423",
    "transaction_status": "የከፋይ ስም/Payer Name",
    "invoice_no": "የክፍያ ቀን/Payment date",
    "payment_date": "የክፍያ ዝርዝር/ Invoice details",
    "settled_amount": "የክፍያ ዝርዝር/ Invoice details",
    "service_fee": "የክፍያ ዝርዝር/ Invoice details",
    "total_paid": "የክፍያ ዝርዝር/ Invoice details",
    "total_in_words": "fifty-one birr and seventy-five cent",
    "payment_mode": "telebirr",
    "payment_reason": "Buy Goods_Chapa",
    "payment_channel": "API/App",
    "customer_note": "",
    "amount": 51.75,
    "transaction_number": "CI83PCZCL3"
  }
}

import requests

url = "http://127.0.0.1:8000/api/v1/wallet/manual/callback/success/"

response = requests.post(url, json=data)

print(response.json())