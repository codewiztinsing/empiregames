import requests

def send_callback(url, payload):
    """
    Sends a POST request to the given callback URL with the provided payload as JSON.

    Args:
        url (str): The callback URL.
        payload (dict): The payload to send.

    Returns:
        response (requests.Response): The response object from the POST request.
    """
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        # Handle/log errors as needed in your application context.
        print(f"Error sending callback: {e}")
        return None

payload ={'session_id': '21b62565-cd51-4d67-8d32-7a437e81874c', 'status': 'success', 'message': 'Transaction verified successfully', 'data': {'payer_name': 'alako abiyo ludago', 'payer_telebirr_no': '2519****1912', 'payer_account_type': 'Individual Customer', 'credited_party': 'AZEB BEHAILU MEKOEN', 'credited_account': '2519****3249', 'transaction_status': 'የከፋይ ስም/Payer Name', 'invoice_no': 'የክፍያ ቀን/Payment date', 'payment_date': 'የክፍያ ዝርዝር/ Invoice details', 'settled_amount': 'የክፍያ ዝርዝር/ Invoice details', 'service_fee': '0.87 Birr', 'total_paid': 'የክፍያ ዝርዝር/ Invoice details', 'total_in_words': 'eleven birr and zero cent', 'payment_mode': 'telebirr', 'payment_reason': 'Send Money to Registered Customer', 'payment_channel': 'API/App', 'customer_note': '', 'amount': 11.0, 'ref_number': 'CJF5HGXUUJ'}, 'payer_telebirr_no': '2519****1912', 'credited_party': 'AZEB BEHAILU MEKOEN', 'amount': 11.0, 'ref_number': 'CJF5HGXUUJ'}

response = send_callback("http://127.0.0.1:8000/api/v1/wallet/manual/callback/success/", payload)
print(response)