data = {
  "session_id": "9a098d29-27aa-4216-9177-2a774d6dcde10",
  "status": "success",
  "message": "Transaction verified successfully",
  "data": {
    "payer_name": "ESHETU FEYESSA ABERA",
    "payer_telebirr_no": "2519****9495",
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
    "amount": 51,
    "ref_number": "CFJ6167JLC"
  }
}
import requests

url = "http://127.0.0.1:8000/api/v1/wallet/manual/callback/success/"
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")