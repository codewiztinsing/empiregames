# base_url = "https://akerbingo.com"
base_url = "http://127.0.0.1:8000"

import requests

def post_manual_callback_success(payload):
    """
    Sends a POST request to /api/v1/wallet/manual/callback/success/ endpoint with the provided payload.

    Args:
        payload (dict): The data to send in the body of the POST request.

    Returns:
        requests.Response: The response object from the server.
    """
    url = f"{base_url}/api/v1/wallet/manual/callback/success/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("\n=== DEBUG: POST manual/callback/success ===")
    print("URL:", url)
    print("Headers:", headers)
    print("Payload:", payload)
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print("Status Code:", response.status_code)
        print("Response Headers:", dict(response.headers))
        print("Response Text:", response.text)
        try:
            print("Response JSON:", response.json())
        except Exception as je:
            print("DEBUG: Failed to parse JSON:", je)
        return response
    except Exception as e:
        print("DEBUG: Request error:", e)
        raise




# payload = {"session_id": "a92b3708-2657-42a6-b759-ed3edc837d74", "status": "success", "message": "Transaction verified successfully", "data": {"payer_name": "alako abiyo ludago", "payer_telebirr_no": "2519****1912", "payer_account_type": "Individual Customer", "credited_party": "AZEB BEHAILU MEKOEN", "credited_account": "2519****3249", "transaction_status": "\u12e8\u12a8\u134b\u12ed \u1235\u121d/Payer Name", "invoice_no": "\u12e8\u12ad\u134d\u12eb \u1240\u1295/Payment date", "payment_date": "\u12e8\u12ad\u134d\u12eb \u12dd\u122d\u12dd\u122d/ Invoice details", "settled_amount": "\u12e8\u12ad\u134d\u12eb \u12dd\u122d\u12dd\u122d/ Invoice details", "service_fee": "0.87 Birr", "total_paid": "\u12e8\u12ad\u134d\u12eb \u12dd\u122d\u12dd\u122d/ Invoice details", "total_in_words": "eleven birr and zero cent", "payment_mode": "telebirr", "payment_reason": "Send Money to Registered Customer", "payment_channel": "API/App", "customer_note": "", "amount": 11.0, "ref_number": "CJF7H9M8DN"}, "payer_telebirr_no": "2519****1912", "credited_party": "AZEB BEHAILU MEKOEN", "amount": 11.0, "ref_number": "CJF7H9M8DN"}
# response = post_manual_callback_success(payload)
# print(response.json())


def post_manual_callback_error(payload):
    """
    Sends a POST request to /api/v1/wallet/manual/callback/error/ endpoint with the provided payload.

    Args:
        payload (dict): The data to send in the body of the POST request.

    Returns:
        requests.Response: The response object from the server.
    """
    url = f"{base_url}/api/v1/wallet/manual/callback/error/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("\n=== DEBUG: POST manual/callback/error ===")
    print("URL:", url)
    print("Headers:", headers)
    print("Payload:", payload)
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print("Status Code:", response.status_code)
        print("Response Headers:", dict(response.headers))
        print("Response Text:", response.text)
        try:
            print("Response JSON:", response.json())
        except Exception as je:
            print("DEBUG: Failed to parse JSON:", je)
        return response
    except Exception as e:
        print("DEBUG: Request error:", e)
        raise

payload = {
    'session_id': 'a92b3708-2657-42a6-b759-ed3edc837d74', 
    'status': 'failed', 
    'message': 'Transaction number already processed', 
    'data': {
        'payer_name': 'alako abiyo ludago', 
        'payer_telebirr_no': '2519****1912', 
        'payer_account_type': 'Individual Customer', 
        'credited_party': 'AZEB BEHAILU MEKOEN', 
        'credited_account': '2519****3249', 
        'transaction_status': 'የከፋይ ስም/Payer Name', 
        'invoice_no': 'የክፍያ ቀን/Payment date', 
        'payment_date': 'የክፍያ ዝርዝር/ Invoice details', 
        'settled_amount': 'የክፍያ ዝርዝር/ Invoice details', 
        'service_fee': '0.87 Birr', 
        'total_paid': 'የክፍያ ዝርዝር/ Invoice details', 
        'total_in_words': 'eleven birr and zero cent', 
        'payment_mode': 'telebirr', 
        'payment_reason': 'Send Money to Registered Customer', 
        'payment_channel': 'API/App', 
        'customer_note': '', 
        'amount': 11.0, 
        'ref_number': 'CJF7H9M8DN'
    }
}
response = post_manual_callback_error(payload)
print(response.json())